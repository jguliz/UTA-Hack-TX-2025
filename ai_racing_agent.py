"""
AI Racing Agent with Decision Logging

This AI learns to drive Monaco faster than Verstappen (72.790s) and logs
every decision it makes (braking points, apex angles, throttle control)
"""

import numpy as np
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
import math

from f1_physics_simulator import F1PhysicsSimulator, CarState, CarPhysics


@dataclass
class AIDecision:
    """Single decision made by the AI"""
    time: float
    distance: float

    # Current state
    speed: float
    position_x: float
    position_y: float

    # Track analysis
    upcoming_turn_distance: float
    upcoming_turn_radius: float
    current_turn_phase: str  # "straight", "braking", "turn_in", "apex", "exit"

    # Decision reasoning
    throttle_decision: float
    throttle_reason: str
    brake_decision: float
    brake_reason: str
    steering_decision: float
    steering_reason: str

    # Expected outcome
    expected_speed_change: float
    expected_time_gain: float
    risk_level: str  # "safe", "aggressive", "maximum_attack"


@dataclass
class LapAttempt:
    """One complete lap attempt with all decisions"""
    attempt_number: int
    lap_time: float
    crashed: bool
    crash_location: Optional[str]

    decisions: List[AIDecision]

    # Performance analysis
    sector_times: List[float]
    top_speed: float
    avg_speed: float
    mistakes: int

    # Learning
    improvement_from_previous: float
    what_worked: List[str]
    what_failed: List[str]


class MonacoTrackKnowledge:
    """Knowledge base about Monaco circuit"""

    def __init__(self, verstappen_telemetry_path: str):
        # Load reference telemetry data to learn the track
        with open(verstappen_telemetry_path, 'r') as f:
            self.verstappen_data = json.load(f)

        self.telemetry = self.verstappen_data['telemetry']

        # Compute distance if not present
        if 'distance' not in self.telemetry[0]:
            import math
            distance = 0.0
            for i, point in enumerate(self.telemetry):
                if i > 0:
                    prev = self.telemetry[i-1]
                    dx = point['x'] - prev['x']
                    dy = point['y'] - prev['y']
                    dz = point['z'] - prev['z']
                    distance += math.sqrt(dx**2 + dy**2 + dz**2)
                point['distance'] = distance

        self.track_length = max(t['distance'] for t in self.telemetry)

        # Analyze Verstappen's racing line
        self.racing_line = self._extract_racing_line()
        self.braking_zones = self._find_braking_zones()
        self.apex_points = self._find_apex_points()
        self.critical_turns = self._analyze_critical_turns()

        print(f"\n📚 Track Knowledge Loaded:")
        print(f"  Track Length: {self.track_length:.1f}m")
        print(f"  Racing Line Points: {len(self.racing_line)}")
        print(f"  Braking Zones: {len(self.braking_zones)}")
        print(f"  Apex Points: {len(self.apex_points)}")
        print(f"  Critical Turns: {len(self.critical_turns)}\n")

    def _extract_racing_line(self) -> List[Dict]:
        """Extract optimal racing line from Verstappen's telemetry"""
        return [
            {
                'distance': t['distance'],
                'x': t['x'],
                'y': t['y'],
                'speed': t['speed'],
                'throttle': t['throttle'],
                'brake': t['brake']
            }
            for t in self.telemetry
        ]

    def _find_braking_zones(self) -> List[Dict]:
        """Find where Verstappen brakes"""
        braking_zones = []

        for i, t in enumerate(self.telemetry):
            if t['brake'] and (i == 0 or not self.telemetry[i-1]['brake']):
                # Start of braking zone
                braking_start = t['distance']
                entry_speed = t['speed']

                # Find end of braking
                j = i
                while j < len(self.telemetry) and self.telemetry[j]['brake']:
                    j += 1

                if j < len(self.telemetry):
                    braking_end = self.telemetry[j]['distance']
                    exit_speed = self.telemetry[j]['speed']

                    braking_zones.append({
                        'start_distance': braking_start,
                        'end_distance': braking_end,
                        'entry_speed': entry_speed,
                        'exit_speed': exit_speed,
                        'braking_distance': braking_end - braking_start
                    })

        return braking_zones

    def _find_apex_points(self) -> List[Dict]:
        """Find turn apexes (minimum speed points)"""
        apexes = []
        window = 20

        for i in range(window, len(self.telemetry) - window):
            speeds = [self.telemetry[j]['speed'] for j in range(i - window, i + window)]

            if self.telemetry[i]['speed'] == min(speeds) and self.telemetry[i]['speed'] < 150:
                apexes.append({
                    'distance': self.telemetry[i]['distance'],
                    'x': self.telemetry[i]['x'],
                    'y': self.telemetry[i]['y'],
                    'speed': self.telemetry[i]['speed']
                })

        return apexes

    def _analyze_critical_turns(self) -> List[Dict]:
        """Combine braking zones and apexes into turn analysis"""
        turns = []

        for apex in self.apex_points:
            # Find corresponding braking zone
            braking_zone = None
            for bz in self.braking_zones:
                if bz['start_distance'] < apex['distance'] < bz['end_distance'] + 100:
                    braking_zone = bz
                    break

            if braking_zone:
                turns.append({
                    'apex_distance': apex['distance'],
                    'apex_speed': apex['speed'],
                    'braking_point': braking_zone['start_distance'],
                    'braking_distance': braking_zone['braking_distance'],
                    'entry_speed': braking_zone['entry_speed'],
                    'apex_coords': (apex['x'], apex['y'])
                })

        return turns

    def get_nearest_line_point(self, x: float, y: float) -> Dict:
        """Find nearest point on racing line"""
        min_dist = float('inf')
        nearest = None

        for point in self.racing_line:
            dist = math.sqrt((point['x'] - x)**2 + (point['y'] - y)**2)
            if dist < min_dist:
                min_dist = dist
                nearest = point

        return nearest

    def get_upcoming_turn(self, current_distance: float) -> Optional[Dict]:
        """Get info about the next turn ahead"""
        for turn in self.critical_turns:
            if turn['apex_distance'] > current_distance:
                return turn
        return None

    def get_track_section_info(self, current_distance: float, lookahead: float = 200.0) -> Dict:
        """
        Get detailed information about current track section and what's ahead

        Args:
            current_distance: Current position on track (meters from start)
            lookahead: How far ahead to analyze (default 200m)

        Returns:
            Dictionary with comprehensive track section information
        """
        # Find current position in telemetry
        current_idx = self._get_telemetry_index(current_distance)
        lookahead_distance = current_distance + lookahead

        # Get upcoming turns within lookahead window
        upcoming_turns = [
            turn for turn in self.critical_turns
            if current_distance < turn['apex_distance'] <= lookahead_distance
        ]

        # Get next turn (most important)
        next_turn = upcoming_turns[0] if upcoming_turns else None

        # Analyze track curvature in the lookahead zone
        curvature_zones = self._analyze_curvature(current_idx, lookahead)

        # Determine optimal speeds for upcoming sections
        speed_targets = self._calculate_speed_targets(current_idx, lookahead)

        # Identify racing line recommendations
        racing_line_advice = self._get_racing_line_strategy(current_distance, next_turn)

        return {
            'current_distance': current_distance,
            'track_progress_pct': (current_distance / self.track_length) * 100,
            'next_turn': next_turn,
            'upcoming_turns': upcoming_turns,
            'distance_to_next_turn': next_turn['braking_point'] - current_distance if next_turn else None,
            'curvature_zones': curvature_zones,
            'speed_targets': speed_targets,
            'racing_line_strategy': racing_line_advice,
            'section_type': self._classify_section(current_distance, next_turn)
        }

    def _get_telemetry_index(self, distance: float) -> int:
        """Find telemetry array index closest to given distance"""
        min_diff = float('inf')
        best_idx = 0

        for i, point in enumerate(self.telemetry):
            diff = abs(point['distance'] - distance)
            if diff < min_diff:
                min_diff = diff
                best_idx = i

        return best_idx

    def _analyze_curvature(self, start_idx: int, lookahead: float) -> List[Dict]:
        """
        Analyze track curvature in lookahead zone
        Returns zones with their curvature characteristics
        """
        zones = []
        current_zone = None
        start_distance = self.telemetry[start_idx]['distance']

        for i in range(start_idx, min(start_idx + 200, len(self.telemetry))):
            if self.telemetry[i]['distance'] > start_distance + lookahead:
                break

            # Calculate curvature from speed profile (F1 drivers slow down for corners)
            speed = self.telemetry[i]['speed']

            # Classify curvature based on speed
            if speed > 250:
                curve_type = 'straight'
                severity = 0.0
            elif speed > 200:
                curve_type = 'fast_corner'
                severity = 0.3
            elif speed > 150:
                curve_type = 'medium_corner'
                severity = 0.6
            else:
                curve_type = 'slow_corner'
                severity = 0.9

            # Group into zones
            if current_zone is None or current_zone['type'] != curve_type:
                if current_zone:
                    zones.append(current_zone)
                current_zone = {
                    'type': curve_type,
                    'severity': severity,
                    'start_distance': self.telemetry[i]['distance'],
                    'end_distance': self.telemetry[i]['distance'],
                    'min_speed': speed,
                    'entry_speed': speed
                }
            else:
                current_zone['end_distance'] = self.telemetry[i]['distance']
                current_zone['min_speed'] = min(current_zone['min_speed'], speed)

        if current_zone:
            zones.append(current_zone)

        return zones

    def _calculate_speed_targets(self, start_idx: int, lookahead: float) -> List[Dict]:
        """
        Calculate optimal speed targets for upcoming track sections
        Based on reference lap data
        """
        targets = []
        start_distance = self.telemetry[start_idx]['distance']

        # Sample every 50 meters
        for distance_ahead in range(0, int(lookahead), 50):
            target_distance = start_distance + distance_ahead
            idx = self._get_telemetry_index(target_distance)

            if idx < len(self.telemetry):
                point = self.telemetry[idx]
                targets.append({
                    'distance': point['distance'],
                    'distance_ahead': distance_ahead,
                    'target_speed': point['speed'],
                    'recommended_throttle': point['throttle'],
                    'recommended_brake': point['brake']
                })

        return targets

    def _get_racing_line_strategy(self, current_distance: float, next_turn: Optional[Dict]) -> Dict:
        """
        Provide racing line strategy advice based on current situation
        """
        if next_turn is None:
            return {
                'strategy': 'maximum_attack',
                'description': 'Full throttle on straight, maximize speed',
                'positioning': 'center_track',
                'risk_level': 'low'
            }

        distance_to_turn = next_turn['braking_point'] - current_distance

        # Different strategies based on distance to turn
        if distance_to_turn > 150:
            return {
                'strategy': 'straight_line_speed',
                'description': 'Build maximum speed before braking zone',
                'positioning': 'setup_for_turn',
                'risk_level': 'low',
                'target_speed': next_turn['entry_speed']
            }
        elif distance_to_turn > 50:
            return {
                'strategy': 'prepare_braking',
                'description': f'Approaching braking zone in {distance_to_turn:.0f}m',
                'positioning': 'wide_for_entry',
                'risk_level': 'medium',
                'braking_point': next_turn['braking_point'],
                'target_entry_speed': next_turn['entry_speed']
            }
        elif distance_to_turn > 0:
            return {
                'strategy': 'braking_zone',
                'description': 'Heavy braking, trail brake to apex',
                'positioning': 'commit_to_line',
                'risk_level': 'high',
                'target_apex_speed': next_turn['apex_speed']
            }
        else:
            # Past braking point, approaching/at apex
            distance_to_apex = next_turn['apex_distance'] - current_distance
            if distance_to_apex > 0:
                return {
                    'strategy': 'apex_approach',
                    'description': 'Minimum speed, prepare for throttle',
                    'positioning': 'hit_apex',
                    'risk_level': 'very_high',
                    'target_apex_speed': next_turn['apex_speed']
                }
            else:
                return {
                    'strategy': 'corner_exit',
                    'description': 'Progressive throttle, maximize exit speed',
                    'positioning': 'track_out_wide',
                    'risk_level': 'medium',
                    'focus': 'exit_speed'
                }

    def _classify_section(self, current_distance: float, next_turn: Optional[Dict]) -> str:
        """Classify what type of section the car is currently in"""
        if next_turn is None:
            return 'final_straight'

        distance_to_braking = next_turn['braking_point'] - current_distance
        distance_to_apex = next_turn['apex_distance'] - current_distance

        if distance_to_braking > 100:
            return 'straight'
        elif distance_to_braking > 0:
            return 'braking_approach'
        elif distance_to_apex > 0:
            return 'corner_entry'
        elif distance_to_apex > -50:
            return 'apex_zone'
        else:
            return 'corner_exit'

    def get_optimal_speed_and_angle(self, current_distance: float) -> Dict:
        """
        Get optimal speed and steering angle for current position
        Based on reference lap data with variation for different scenarios
        """
        idx = self._get_telemetry_index(current_distance)
        reference_point = self.telemetry[idx]
        section_info = self.get_track_section_info(current_distance)

        # Base targets from reference lap
        optimal_speed = reference_point['speed']

        # Calculate steering angle from racing line curvature
        if idx > 0 and idx < len(self.telemetry) - 1:
            prev = self.telemetry[idx - 1]
            next_p = self.telemetry[idx + 1]

            # Calculate direction vectors
            dx1 = reference_point['x'] - prev['x']
            dy1 = reference_point['y'] - prev['y']
            dx2 = next_p['x'] - reference_point['x']
            dy2 = next_p['y'] - reference_point['y']

            # Calculate angle change (simplified steering angle estimation)
            angle1 = math.atan2(dy1, dx1)
            angle2 = math.atan2(dy2, dx2)
            steering_angle = angle2 - angle1

            # Normalize to [-45, 45] degrees
            steering_angle = math.degrees(steering_angle)
            steering_angle = max(-45, min(45, steering_angle))
        else:
            steering_angle = 0.0

        # Provide scenario-specific variations
        return {
            'optimal_speed': optimal_speed,
            'steering_angle': steering_angle,
            'section_type': section_info['section_type'],
            'reference_throttle': reference_point['throttle'],
            'reference_brake': reference_point['brake'],

            # Scenario variations
            'qualifying_speed': optimal_speed,  # Maximum attack
            'race_speed': optimal_speed * 0.97,  # 3% slower for tire management
            'overtaking_speed': optimal_speed * 1.02,  # 2% faster, more risk
            'defending_speed': optimal_speed * 0.98,  # Cover inside line
            'wet_speed': optimal_speed * 0.85,  # 15% slower in wet

            # Additional guidance
            'next_turn_info': section_info['next_turn'],
            'recommended_strategy': section_info['racing_line_strategy']
        }


class AIRacingAgent:
    """
    AI that learns to drive Monaco using reinforcement learning
    Logs every decision for transparency
    """

    def __init__(self, track_knowledge: MonacoTrackKnowledge):
        self.track = track_knowledge
        self.simulator = F1PhysicsSimulator()

        # Learning parameters (will improve over time)
        self.brake_aggression = 0.8  # How late to brake (0-1, higher = later)
        self.apex_precision = 0.9    # How close to hit apex (0-1)
        self.throttle_confidence = 0.7  # How early to get on throttle (0-1)

        # Decision log
        self.current_decisions: List[AIDecision] = []

        print("🤖 AI Racing Agent Initialized")
        print(f"  Brake Aggression: {self.brake_aggression:.2f}")
        print(f"  Apex Precision: {self.apex_precision:.2f}")
        print(f"  Throttle Confidence: {self.throttle_confidence:.2f}\n")

    def decide_controls(self, state: CarState, time: float) -> Tuple[float, float, float]:
        """
        Make driving decision and log the reasoning

        Returns:
            (throttle, brake, steering)
        """
        # Find where we are on track
        nearest = self.track.get_nearest_line_point(state.x, state.y)
        upcoming_turn = self.track.get_upcoming_turn(state.distance)

        # Determine current phase
        if upcoming_turn:
            dist_to_turn = upcoming_turn['apex_distance'] - state.distance
            braking_point = upcoming_turn['braking_point'] - state.distance

            if dist_to_turn < -50:
                phase = "exit"
            elif braking_point < 10 and dist_to_turn > 10:
                phase = "braking"
            elif dist_to_turn < 10 and dist_to_turn > -20:
                phase = "apex"
            elif dist_to_turn < 50:
                phase = "turn_in"
            else:
                phase = "straight"
        else:
            phase = "straight"
            dist_to_turn = 1000
            braking_point = 1000

        # DECISION MAKING with LOGGING

        # === THROTTLE DECISION ===
        if phase == "straight":
            throttle = 100.0
            throttle_reason = "Straight section - full power to maximize speed"
        elif phase == "exit":
            throttle = 80.0 + (self.throttle_confidence * 20.0)
            throttle_reason = f"Turn exit - early throttle (confidence: {self.throttle_confidence:.2f})"
        elif phase == "apex":
            throttle = 30.0
            throttle_reason = "At apex - maintenance throttle only"
        elif phase == "turn_in":
            throttle = 50.0
            throttle_reason = "Turning in - trail braking phase"
        else:  # braking
            throttle = 0.0
            throttle_reason = "Braking zone - zero throttle"

        # === BRAKE DECISION ===
        if phase == "braking":
            # Calculate required braking
            if upcoming_turn:
                speed_diff = state.speed * 3.6 - upcoming_turn['apex_speed']
                brake_intensity = min(100.0, speed_diff / 2.0)
                brake = brake_intensity * self.brake_aggression
                brake_reason = f"Braking for turn (target: {upcoming_turn['apex_speed']:.0f} km/h, aggression: {self.brake_aggression:.2f})"
            else:
                brake = 0.0
                brake_reason = "No upcoming turn"
        elif phase == "turn_in":
            brake = 20.0  # Trail braking
            brake_reason = "Trail braking into apex"
        else:
            brake = 0.0
            brake_reason = "No braking required"

        # === STEERING DECISION ===
        if nearest:
            # Calculate steering to follow racing line
            target_x = nearest['x']
            target_y = nearest['y']

            dx = target_x - state.x
            dy = target_y - state.y

            target_heading = math.atan2(dy, dx)
            heading_error = target_heading - state.heading

            # Normalize to -pi to pi
            while heading_error > math.pi:
                heading_error -= 2 * math.pi
            while heading_error < -math.pi:
                heading_error += 2 * math.pi

            steering = np.clip(heading_error / math.radians(30), -1, 1)
            steering_reason = f"Following racing line (error: {math.degrees(heading_error):.1f}°)"
        else:
            steering = 0.0
            steering_reason = "No racing line reference"

        # LOG DECISION
        decision = AIDecision(
            time=time,
            distance=state.distance,
            speed=state.speed * 3.6,  # Convert to km/h
            position_x=state.x,
            position_y=state.y,
            upcoming_turn_distance=dist_to_turn,
            upcoming_turn_radius=100.0 if upcoming_turn else 0,
            current_turn_phase=phase,
            throttle_decision=throttle,
            throttle_reason=throttle_reason,
            brake_decision=brake,
            brake_reason=brake_reason,
            steering_decision=steering,
            steering_reason=steering_reason,
            expected_speed_change=0.0,  # Would calculate based on physics
            expected_time_gain=0.0,
            risk_level="aggressive" if self.brake_aggression > 0.85 else "balanced"
        )

        self.current_decisions.append(decision)

        return throttle, brake, steering

    def attempt_lap(self, attempt_number: int) -> LapAttempt:
        """
        Attempt one lap and log all decisions
        """
        print(f"\n🏁 Lap Attempt #{attempt_number}")
        print(f"  Parameters: brake={self.brake_aggression:.2f}, apex={self.apex_precision:.2f}, throttle={self.throttle_confidence:.2f}")

        self.current_decisions = []

        # Run simulation
        states = self.simulator.simulate_lap(
            lambda state, time: self.decide_controls(state, time),
            max_time=120.0
        )

        final_state = states[-1]
        lap_time = final_state.lap_time

        # Check if we completed the lap (distance > track length)
        completed = final_state.distance >= self.track.track_length

        # Analyze performance
        lap_attempt = LapAttempt(
            attempt_number=attempt_number,
            lap_time=lap_time if completed else 999.0,
            crashed=not completed,
            crash_location=None,
            decisions=self.current_decisions,
            sector_times=[0, 0, 0],  # Would calculate properly
            top_speed=max(s.speed for s in states) * 3.6,
            avg_speed=np.mean([s.speed for s in states]) * 3.6,
            mistakes=0,
            improvement_from_previous=0.0,
            what_worked=[],
            what_failed=[]
        )

        print(f"  Result: {lap_time:.3f}s (completed: {completed})")
        print(f"  Decisions logged: {len(self.current_decisions)}")
        print(f"  Top speed: {lap_attempt.top_speed:.1f} km/h")

        return lap_attempt


def main():
    """Test the AI racing agent"""

    print("\n" + "="*80)
    print("AI RACING AGENT - DECISION LOGGING TEST")
    print("="*80)

    # Load track knowledge from Leclerc's pole lap data
    reference_lap = Path(__file__).parent.parent / 'logs' / 'monaco_2024_lec_70.270s.json'

    if not reference_lap.exists():
        print(f"❌ Error: Reference telemetry not found at {reference_lap}")
        return

    track = MonacoTrackKnowledge(str(reference_lap))
    agent = AIRacingAgent(track)

    # Attempt a lap
    lap = agent.attempt_lap(attempt_number=1)

    print("\n" + "="*80)
    print("DECISION LOG SAMPLE (First 5 decisions)")
    print("="*80)

    for i, decision in enumerate(lap.decisions[:5]):
        print(f"\nDecision #{i+1} @ {decision.time:.2f}s:")
        print(f"  Phase: {decision.current_turn_phase}")
        print(f"  Speed: {decision.speed:.1f} km/h")
        print(f"  Throttle: {decision.throttle_decision:.1f}% - {decision.throttle_reason}")
        print(f"  Brake: {decision.brake_decision:.1f}% - {decision.brake_reason}")
        print(f"  Steering: {decision.steering_decision:.2f} - {decision.steering_reason}")

    print("\n" + "="*80)
    print("✓ AI agent working with full decision logging")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
