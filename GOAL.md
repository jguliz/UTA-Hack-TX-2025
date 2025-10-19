# F1 Racing AI - HackTX 2025 Goals

## 🎯 Primary Objective
Build an AI that can complete a full lap of Monaco Circuit faster than professional F1 drivers using reinforcement learning and realistic physics simulation.

## 🏎️ Core Requirements

### 1. Realistic F1 Physics Simulation
- **Accurate Car Specifications**
  - Mass: 798 kg (2024 minimum weight)
  - Power: 950 HP (ICE + ERS)
  - Acceleration: 0-100 km/h in 2.6 seconds
  - Top Speed: 350+ km/h
  - Tire compounds: SOFT, MEDIUM, HARD with realistic degradation
  - Downforce and drag modeling
  - Traction control and brake systems

- **Physical Forces**
  - Longitudinal acceleration/deceleration
  - Lateral grip and cornering forces
  - Weight transfer dynamics
  - Tire temperature and wear effects

### 2. AI Training System
- **Reinforcement Learning (PPO)**
  - Policy network (Actor-Critic architecture)
  - State space: position, speed, heading, tire info, upcoming turns
  - Action space: throttle, brake, steering
  - Reward shaping for lap completion

- **Training Phases**
  - Phase 1: Learn to move and accelerate (COMPLETE ✅)
  - Phase 2: Learn to stay on track and follow racing line (IN PROGRESS 🔄)
  - Phase 3: Learn to go fast and optimize lap times (PENDING ⏳)

### 3. Track Knowledge & Awareness
- **Monaco Circuit Data**
  - Official FastF1 telemetry from 2024 race
  - Charles Leclerc reference lap: 70.270s
  - True track boundaries from multi-year extreme points analysis
  - 19 critical turns with braking/apex/exit points

- **Real-time Track Intelligence**
  - Current position along racing line
  - Upcoming turn detection (200m lookahead)
  - Optimal speed and steering angle per section
  - Track curvature analysis
  - Multiple racing strategies (qualifying, race pace, overtaking, defending, wet)

### 4. Performance Targets
- **Baseline**: Match Leclerc's 70.270s qualifying lap
- **Goal**: Beat Leclerc by 0.5-1.0 seconds
- **Stretch Goal**: Sub-70 second lap time

## 🚀 Current Progress

### Phase 1: Movement Mastery ✅
- ✅ AI can accelerate from rolling start (30 km/h)
- ✅ Reaches F1-level speeds (200+ km/h)
- ✅ Sustains high average speeds (164 km/h)
- ✅ Runs for extended periods (29 seconds / 2,907 steps)
- ✅ Physical movement tracking implemented

### Phase 2: Track Following 🔄
- 🔄 AI explores environment but goes off-track
- 🔄 Distance along racing line: 0m (not following optimal path)
- 🔄 Crash reason: "off_track" (needs better line-following rewards)

### Next Steps
1. **Improve Reward Shaping**
   - Increase rewards for staying close to racing line
   - Add penalties for drifting away from optimal path
   - Balance speed rewards with positioning rewards

2. **Curriculum Learning**
   - Start with wider track boundaries (forgiving)
   - Gradually tighten boundaries as AI improves
   - Progressive difficulty scaling

3. **State Space Enhancement**
   - Add more lookahead information
   - Include lateral position relative to racing line
   - Add racing line curvature in upcoming sections

## 📊 Training Infrastructure

### Real-time Dashboard
- Live training metrics (episodes, crashes, rewards)
- Episode-by-episode analysis
- Training evolution over time
- Crash statistics and patterns
- Auto-refresh every 3 seconds

### Data Collection
- Episode position history (every 10 steps)
- Crash locations and reasons
- Speed, distance, and trajectory data
- Training checkpoints every 100 episodes

## 🔧 Technical Architecture

### Files
- `train.py` - Main RL trainer (PPO algorithm)
- `ai_racing_agent.py` - Track knowledge and racing intelligence
- `f1_physics_simulator.py` - Realistic physics engine
- `app.py` - Flask dashboard server
- `logs/` - Training data and episodes
- `models/` - Saved AI checkpoints

### Training Configuration
- Episodes: 2000
- Max steps per episode: 10,000 (100 seconds)
- Learning rate: 3e-4
- Stuck detection: 500 steps (5 seconds)
- Starting speed: 30 km/h (safety car start)

## 🎮 Key Features

### AI Capabilities
- Real-time track position awareness
- Turn-by-turn speed optimization
- Multiple racing scenarios (qualifying, race, overtaking, defending, wet)
- Adaptive strategy based on track section

### Track Analysis
- 19 critical turns identified
- Braking points calculated
- Apex speeds determined
- Exit strategies defined
- Track curvature zones mapped

## 🏁 Success Criteria
1. ✅ AI completes full Monaco lap without crashing
2. ⏳ Lap time under 72 seconds (better than average F1 driver)
3. 🎯 Lap time under 70.270s (beats Leclerc)
4. 🚀 Lap time under 70s (superhuman performance)

---

**Last Updated**: October 19, 2025
**Status**: Phase 2 - Track Following (In Progress)
