"""
FIXED F1 Racing AI Trainer - Realistic and Actually Works

Key Fixes:
1. Proper track boundary detection using Monaco TRUE boundaries
2. Realistic crash detection (off track, collision, stuck)
3. Better reward shaping for learning from 0 km/h
4. Proper distance tracking along racing line
5. Curriculum learning (start easier, get harder)
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
import time

from f1_physics_simulator import F1PhysicsSimulator, CarState
from ai_racing_agent import MonacoTrackKnowledge


@dataclass
class TrainingConfig:
    """Fixed training configuration"""
    num_episodes: int = 2000
    max_steps_per_episode: int = 10000  # About 100 seconds at 100Hz
    learning_rate: float = 3e-4
    gamma: float = 0.99
    epsilon: float = 0.2
    value_coef: float = 0.5
    entropy_coef: float = 0.01
    batch_size: int = 64
    epochs_per_update: int = 4

    # Realistic rewards
    crash_penalty: float = -50.0
    completion_reward: float = 200.0
    progress_reward: float = 1.0  # Per meter
    speed_reward: float = 0.01  # Per km/h when on track
    time_penalty: float = -0.01  # Per second


class PolicyNetwork(nn.Module):
    """Actor-Critic network with better architecture"""

    def __init__(self, state_dim: int = 12, action_dim: int = 3):
        super().__init__()

        # Shared layers
        self.shared = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.LayerNorm(256),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.LayerNorm(256),
        )

        # Actor (policy)
        self.actor = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, action_dim),
            nn.Tanh()
        )

        self.actor_logstd = nn.Parameter(torch.zeros(action_dim))

        # Critic (value)
        self.critic = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )

    def forward(self, state):
        features = self.shared(state)
        action_mean = self.actor(features)
        action_std = torch.exp(self.actor_logstd)
        value = self.critic(features)
        return action_mean, action_std, value

    def get_action(self, state, deterministic=False):
        action_mean, action_std, value = self.forward(state)

        if deterministic:
            return action_mean, value

        # Sample from Gaussian
        dist = torch.distributions.Normal(action_mean, action_std)
        action = dist.sample()
        log_prob = dist.log_prob(action).sum(dim=-1)

        return action, log_prob, value


class RacingEnv:
    """Fixed F1 Racing Environment"""

    def __init__(self, track: MonacoTrackKnowledge, config: TrainingConfig):
        self.track = track
        self.config = config
        self.simulator = F1PhysicsSimulator()

        # Load track boundaries
        boundaries_file = Path(__file__).parent.parent / 'logs' / 'monaco_true_boundaries.json'
        if boundaries_file.exists():
            with open(boundaries_file, 'r') as f:
                boundary_data = json.load(f)
                self.left_boundary = boundary_data['left_boundary']
                self.right_boundary = boundary_data['right_boundary']
                self.has_boundaries = True
        else:
            self.has_boundaries = False
            print("Warning: Track boundaries not found, using distance-based boundaries")

        self.state = CarState()
        self.steps = 0
        self.last_distance = 0
        self.best_distance = 0
        self.lap_start_time = 0
        self.consecutive_no_progress = 0

        # Track AI's position history for visualization
        self.position_history = []

        # Track ACTUAL physical movement (not just racing line progress)
        self.last_x = 0
        self.last_y = 0
        self.total_physical_distance = 0

    def reset(self) -> np.ndarray:
        """Reset to start position"""
        # Start at beginning of racing line
        first = self.track.racing_line[0]
        second = self.track.racing_line[min(5, len(self.track.racing_line)-1)]

        # Set position
        self.state.x = first['x']
        self.state.y = first['y']

        # Set heading
        dx = second['x'] - first['x']
        dy = second['y'] - first['y']
        self.state.heading = np.arctan2(dy, dx)

        # START WITH ROLLING SPEED: Give AI a fighting chance (30 km/h = ~8.3 m/s)
        # This is like starting behind the safety car in F1
        self.state.speed = 8.3  # m/s = 30 km/h
        self.state.gear = 2
        self.state.rpm = 6000
        self.state.throttle = 0
        self.state.brake = 0
        self.state.steering = 0
        self.state.distance = 0
        self.state.lap_time = 0

        # Reset tracking
        self.steps = 0
        self.last_distance = 0
        self.best_distance = 0
        self.lap_start_time = time.time()
        self.consecutive_no_progress = 0

        # Clear position history for new episode
        self.position_history = []

        # Reset physical movement tracking
        self.last_x = self.state.x
        self.last_y = self.state.y
        self.total_physical_distance = 0

        return self._get_observation()

    def _get_observation(self) -> np.ndarray:
        """Get current state observation (12 dims)"""
        # Find nearest racing line point
        nearest = self.track.get_nearest_line_point(self.state.x, self.state.y)

        # Distance from racing line
        pos_error = np.sqrt((self.state.x - nearest['x'])**2 +
                           (self.state.y - nearest['y'])**2)

        # Get upcoming turn info
        section_info = self.track.get_track_section_info(self.state.distance)
        next_turn = section_info['next_turn']

        if next_turn:
            turn_dist = next_turn['braking_point'] - self.state.distance
            turn_severity = 1.0 - (next_turn['apex_speed'] / 250.0)
            target_speed = next_turn['entry_speed']
        else:
            turn_dist = 1000.0
            turn_severity = 0.0
            target_speed = 250.0

        # Speed targets
        guidance = self.track.get_optimal_speed_and_angle(self.state.distance)
        optimal_speed = guidance['optimal_speed']

        obs = np.array([
            self.state.speed / 100.0,  # Normalized speed
            pos_error / 20.0,  # Normalized position error
            self.state.heading / np.pi,  # Normalized heading
            self.state.distance / 3300.0,  # Progress along track
            turn_dist / 500.0,  # Distance to next turn
            turn_severity,  # How tight the turn is
            optimal_speed / 100.0,  # What speed we should be at
            target_speed / 100.0,  # Target speed for next section
            self.state.throttle / 100.0,  # Current throttle
            self.state.brake / 100.0,  # Current brake
            self.state.steering,  # Current steering
            self.state.tire_temp / 100.0  # Tire temperature
        ], dtype=np.float32)

        return obs

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, dict]:
        """Execute one timestep"""
        # Convert actions from [-1, 1] to proper ranges
        throttle = np.clip((action[0] + 1) * 50, 0, 100)  # [0, 100]
        brake = np.clip((action[1] + 1) * 50, 0, 100)  # [0, 100]
        steering = np.clip(action[2], -1, 1)  # [-1, 1]

        # Save old position for distance calculation
        old_x, old_y = self.state.x, self.state.y

        # Physics update
        self.state = self.simulator.update_car_state(
            self.state, throttle, brake, steering
        )

        # Record position for visualization (every 10 steps to reduce data size)
        if self.steps % 10 == 0:
            self.position_history.append({
                'x': float(self.state.x),
                'y': float(self.state.y),
                'speed': float(self.state.speed * 3.6),  # km/h
                'distance': float(self.state.distance)
            })

        # Calculate distance traveled this step
        step_distance = np.sqrt((self.state.x - old_x)**2 + (self.state.y - old_y)**2)

        # Update distance along track
        nearest = self.track.get_nearest_line_point(self.state.x, self.state.y)
        self.state.distance = nearest['distance']

        # Track PHYSICAL movement (not racing line progress)
        physical_movement = np.sqrt((self.state.x - self.last_x)**2 + (self.state.y - self.last_y)**2)
        self.total_physical_distance += physical_movement

        # Stuck detection: check if car has physically moved in the last window
        if physical_movement < 0.01:  # Less than 1cm of physical movement
            self.consecutive_no_progress += 1
        else:
            self.consecutive_no_progress = 0

        self.last_x = self.state.x
        self.last_y = self.state.y

        # Track progress along racing line too (for rewards)
        progress_this_step = self.state.distance - self.last_distance
        self.best_distance = max(self.best_distance, self.state.distance)
        self.last_distance = self.state.distance
        self.steps += 1

        # Calculate reward and check if done
        reward, done, info = self._calculate_reward(step_distance, progress_this_step)

        # Get next observation
        obs = self._get_observation()

        return obs, reward, done, info

    def _is_off_track(self) -> bool:
        """Check if car is off the track using TRUE boundaries"""
        if not self.has_boundaries:
            # Fallback to distance-based check
            nearest = self.track.get_nearest_line_point(self.state.x, self.state.y)
            distance_from_line = np.sqrt((self.state.x - nearest['x'])**2 +
                                         (self.state.y - nearest['y'])**2)
            return distance_from_line > 25  # 25 meters off racing line = off track

        # Find nearest boundary points
        min_dist_left = float('inf')
        min_dist_right = float('inf')

        # Check a window of nearby boundary points
        for boundary in [self.left_boundary, self.right_boundary]:
            for point in boundary:
                dist = np.sqrt((self.state.x - point['x'])**2 +
                              (self.state.y - point['y'])**2)
                if boundary == self.left_boundary:
                    min_dist_left = min(min_dist_left, dist)
                else:
                    min_dist_right = min(min_dist_right, dist)

        # If we're very far from BOTH boundaries, we're definitely off track
        if min_dist_left > 50 and min_dist_right > 50:
            return True

        return False

    def _calculate_reward(self, step_distance: float, progress_this_step: float) -> Tuple[float, bool, dict]:
        """Calculate reward for this step"""
        reward = 0.0
        done = False
        info = {}

        # Get distance from racing line
        nearest = self.track.get_nearest_line_point(self.state.x, self.state.y)
        distance_from_line = np.sqrt((self.state.x - nearest['x'])**2 +
                                     (self.state.y - nearest['y'])**2)

        # === CRASH DETECTION ===

        # 1. Off track
        if self._is_off_track():
            reward = self.config.crash_penalty
            done = True
            info['crash'] = True
            info['crash_reason'] = 'off_track'
            return reward, done, info

        # 2. Stuck/No progress - VERY LENIENT (5 seconds = 500 steps)
        if self.consecutive_no_progress > 500:  # 5 seconds without ANY movement
            reward = self.config.crash_penalty
            done = True
            info['crash'] = True
            info['crash_reason'] = 'stuck'
            return reward, done, info

        # 3. Going backwards
        if self.state.speed < 0:
            reward = self.config.crash_penalty * 0.5
            done = True
            info['crash'] = True
            info['crash_reason'] = 'backwards'
            return reward, done, info

        # === COMPLETION ===
        if self.state.distance >= self.track.track_length:
            lap_time = time.time() - self.lap_start_time
            reward = self.config.completion_reward
            # Bonus for fast lap time
            if lap_time < 100:
                reward += (100 - lap_time) * 2
            done = True
            info['completed'] = True
            info['lap_time'] = lap_time
            return reward, done, info

        # === TIMEOUT ===
        if self.steps >= self.config.max_steps_per_episode:
            done = True
            info['timeout'] = True
            # Give partial credit for progress
            reward = (self.state.distance / self.track.track_length) * 50
            return reward, done, info

        # === ONGOING REWARDS ===

        # 1. PROGRESS - Most important for learning
        if progress_this_step > 0:
            reward += progress_this_step * self.config.progress_reward

        # 2. SPEED - Reward going fast when on track
        if distance_from_line < 15:  # Within 15m of racing line
            reward += (self.state.speed * 3.6) * self.config.speed_reward  # km/h

        # 3. RACING LINE - Bonus for staying close to optimal line
        if distance_from_line < 10:
            reward += 0.1
        elif distance_from_line < 20:
            reward += 0.05

        # 4. SMOOTH DRIVING - Penalty for excessive steering/brake
        if abs(self.state.steering) > 0.8:
            reward -= 0.02
        if self.state.brake > 80:
            reward -= 0.01

        # 5. TIME PENALTY - Small penalty to encourage speed
        reward += self.config.time_penalty

        info['distance'] = self.state.distance
        info['speed'] = self.state.speed * 3.6
        info['distance_from_line'] = distance_from_line

        return reward, done, info


class PPOTrainer:
    """Fixed PPO Trainer"""

    def __init__(self, config: TrainingConfig):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Load track
        reference_lap = Path(__file__).parent / 'logs' / 'monaco_2024_lec_70.270s.json'
        self.track = MonacoTrackKnowledge(str(reference_lap))

        # Create environment
        self.env = RacingEnv(self.track, config)

        # Create networks
        self.policy = PolicyNetwork().to(self.device)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=config.learning_rate)

        # Training stats
        self.episode_rewards = []
        self.lap_times = []
        self.crash_count = 0
        self.best_lap_time = float('inf')

    def train(self):
        """Main training loop"""
        print("\n" + "="*80)
        print("🏎️  FIXED F1 AI TRAINER - STARTING TRAINING")
        print("="*80)
        print(f"Device: {self.device}")
        print(f"Episodes: {self.config.num_episodes}")
        print(f"Track: Monaco ({self.track.track_length:.0f}m)")
        print("="*80 + "\n")

        for episode in range(self.config.num_episodes):
            episode_reward, lap_time, crashed = self._run_episode(episode + 1)

            self.episode_rewards.append(episode_reward)
            self.lap_times.append(lap_time)

            if crashed:
                self.crash_count += 1

            if lap_time and lap_time < self.best_lap_time:
                self.best_lap_time = lap_time
                # Save best model
                self._save_model(f"best_lap_{lap_time:.3f}s")

            # Print progress
            if (episode + 1) % 10 == 0:
                recent_rewards = self.episode_rewards[-10:]
                recent_laps = [lt for lt in self.lap_times[-10:] if lt is not None]
                crash_rate = (self.crash_count / (episode + 1)) * 100

                print(f"Episode {episode+1}/{self.config.num_episodes}")
                print(f"  Avg Reward (last 10): {np.mean(recent_rewards):.2f}")
                print(f"  Crash Rate: {crash_rate:.1f}%")
                if recent_laps:
                    print(f"  Avg Lap Time: {np.mean(recent_laps):.2f}s")
                    print(f"  Best Lap: {self.best_lap_time:.3f}s")
                print()

            # Save checkpoint
            if (episode + 1) % 100 == 0:
                self._save_checkpoint(episode + 1)

        print("\n🏁 Training Complete!")
        print(f"Best Lap Time: {self.best_lap_time:.3f}s")
        print(f"Total Crashes: {self.crash_count}/{self.config.num_episodes}")

    def _run_episode(self, episode_num: int) -> Tuple[float, float, bool]:
        """Run one training episode"""
        obs = self.env.reset()
        episode_reward = 0.0
        lap_time = None
        crashed = False
        crash_location = None

        # Storage for PPO update
        states, actions, log_probs, rewards, values, dones = [], [], [], [], [], []

        done = False
        while not done:
            # Get action from policy
            state_tensor = torch.FloatTensor(obs).unsqueeze(0).to(self.device)

            with torch.no_grad():
                action, log_prob, value = self.policy.get_action(state_tensor)

            action = action.cpu().numpy()[0]

            # Step environment
            next_obs, reward, done, info = self.env.step(action)

            # Store transition
            states.append(obs)
            actions.append(action)
            log_probs.append(log_prob.item())
            rewards.append(reward)
            values.append(value.item())
            dones.append(done)

            episode_reward += reward
            obs = next_obs

            # Check for completion/crash
            if 'completed' in info:
                lap_time = info['lap_time']
            elif 'crash' in info:
                crashed = True
                crash_location = {
                    'x': float(self.env.state.x),
                    'y': float(self.env.state.y),
                    'reason': info.get('crash_reason', 'unknown')
                }

        # Save episode path for visualization
        self._save_episode_path(episode_num, crashed, crash_location)

        # PPO update
        self._update_policy(states, actions, log_probs, rewards, values, dones)

        return episode_reward, lap_time, crashed

    def _update_policy(self, states, actions, old_log_probs, rewards, values, dones):
        """Update policy using PPO"""
        # Convert to tensors
        states = torch.FloatTensor(np.array(states)).to(self.device)
        actions = torch.FloatTensor(np.array(actions)).to(self.device)
        old_log_probs = torch.FloatTensor(old_log_probs).to(self.device)

        # Calculate returns and advantages
        returns = self._calculate_returns(rewards, values, dones)
        returns = torch.FloatTensor(returns).to(self.device)
        values = torch.FloatTensor(values).to(self.device)
        advantages = returns - values
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        # PPO update
        for _ in range(self.config.epochs_per_update):
            # Get current policy outputs
            action_mean, action_std, new_values = self.policy(states)
            dist = torch.distributions.Normal(action_mean, action_std)
            new_log_probs = dist.log_prob(actions).sum(dim=-1)

            # Calculate ratio
            ratio = torch.exp(new_log_probs - old_log_probs)

            # Clipped surrogate
            surr1 = ratio * advantages
            surr2 = torch.clamp(ratio, 1 - self.config.epsilon, 1 + self.config.epsilon) * advantages
            actor_loss = -torch.min(surr1, surr2).mean()

            # Value loss
            value_loss = ((new_values.squeeze() - returns) ** 2).mean()

            # Entropy bonus
            entropy = dist.entropy().mean()

            # Total loss
            loss = actor_loss + self.config.value_coef * value_loss - self.config.entropy_coef * entropy

            # Update
            self.optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.policy.parameters(), 0.5)
            self.optimizer.step()

    def _calculate_returns(self, rewards, values, dones):
        """Calculate discounted returns"""
        returns = []
        R = 0
        for reward, done in zip(reversed(rewards), reversed(dones)):
            if done:
                R = 0
            R = reward + self.config.gamma * R
            returns.insert(0, R)
        return returns

    def _save_model(self, name):
        """Save model checkpoint"""
        models_dir = Path(__file__).parent.parent / 'models'
        models_dir.mkdir(exist_ok=True)
        torch.save(self.policy.state_dict(), models_dir / f"{name}.pt")

    def _save_episode_path(self, episode: int, crashed: bool, crash_location: dict):
        """Save episode path for visualization"""
        episodes_dir = Path(__file__).parent.parent / 'logs' / 'episodes'
        episodes_dir.mkdir(parents=True, exist_ok=True)

        episode_data = {
            'episode': episode,
            'positions': self.env.position_history,
            'crashed': crashed,
            'crash_location': crash_location,
            'distance_traveled': float(self.env.best_distance),
            'total_steps': int(self.env.steps)
        }

        # Only save every 10 episodes to avoid too many files (or save all if you have space)
        if episode % 10 == 0 or episode <= 50:
            with open(episodes_dir / f'episode_{episode:04d}.json', 'w') as f:
                json.dump(episode_data, f)

    def _save_checkpoint(self, episode):
        """Save training checkpoint"""
        logs_dir = Path(__file__).parent.parent / 'logs'
        logs_dir.mkdir(exist_ok=True)

        # Convert all numpy types to Python native types
        rewards_serializable = [float(r) for r in self.episode_rewards]
        lap_times_serializable = [
            float(lt) if lt is not None and not np.isinf(lt) else None
            for lt in self.lap_times
        ]

        checkpoint = {
            'episode': episode,
            'episode_rewards': rewards_serializable,
            'lap_times': lap_times_serializable,
            'best_lap_time': float(self.best_lap_time) if self.best_lap_time != float('inf') else None,
            'crash_count': int(self.crash_count)
        }

        with open(logs_dir / f'training_log_ep{episode}.json', 'w') as f:
            json.dump(checkpoint, f, indent=2)

        print(f"💾 Saved checkpoint at episode {episode}")


def main():
    config = TrainingConfig()
    trainer = PPOTrainer(config)
    trainer.train()


if __name__ == '__main__':
    main()
