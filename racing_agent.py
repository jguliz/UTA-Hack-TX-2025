"""
AI Racing Agent - Autonomous F1 Strategy AI
Competes against real F1 drivers by making pit stop decisions
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import json
from datetime import datetime
from tire_model import TireDegradationModel
from pit_optimizer import PitStopOptimizer, RaceState
from data_processor import F1DataProcessor


@dataclass
class AIDriverState:
    """State of the AI racing agent"""
    driver_name: str = "AI_RACER"
    team: str = "HackTX Racing"
    current_lap: int = 0
    current_position: int = 20  # Start at back of grid
    tire_compound: str = "MEDIUM"
    tire_life: int = 0
    total_time: float = 0.0  # Cumulative race time
    pit_stops: List[Dict] = field(default_factory=list)
    decision_log: List[Dict] = field(default_factory=list)
    lap_times: List[float] = field(default_factory=list)
    positions: List[int] = field(default_factory=list)


@dataclass
class RaceEvent:
    """Logged race event for replay"""
    lap: int
    timestamp: float
    event_type: str  # 'lap', 'pit_decision', 'position_change', 'overtake'
    driver: str
    data: Dict


class RacingAI:
    """AI agent that races against real F1 drivers"""

    def __init__(self, tire_model: TireDegradationModel,
                 optimizer: PitStopOptimizer,
                 strategy_params: Dict = None):
        """
        Initialize AI racing agent

        Args:
            tire_model: Trained tire degradation model
            optimizer: Pit stop optimizer
            strategy_params: Custom strategy parameters (aggression, risk tolerance, etc.)
        """
        self.tire_model = tire_model
        self.optimizer = optimizer
        self.strategy_params = strategy_params or {
            'aggression': 0.7,  # 0-1, higher = more aggressive pit strategy
            'risk_tolerance': 0.5,  # 0-1, higher = willing to take more risks
            'tire_preference': 'MEDIUM',  # Starting tire preference
            'learning_rate': 0.1  # How much to adjust strategy after each race
        }

        self.ai_state = None
        self.race_events = []
        self.race_results_history = []

    def initialize_race(self, race_name: str, total_laps: int,
                       starting_position: int = 20,
                       starting_compound: str = "MEDIUM") -> None:
        """
        Initialize AI for a new race

        Args:
            race_name: Name of the race
            total_laps: Total race laps
            starting_position: Grid position (default: 20 = back of grid)
            starting_compound: Starting tire compound
        """
        self.ai_state = AIDriverState(
            current_position=starting_position,
            tire_compound=starting_compound,
            tire_life=0
        )
        self.race_events = []

        # Log race start
        self._log_event(
            lap=0,
            event_type='race_start',
            data={
                'race': race_name,
                'starting_position': starting_position,
                'starting_tire': starting_compound,
                'strategy_params': self.strategy_params
            }
        )

    def simulate_lap(self, lap_number: int, race_data: pd.DataFrame) -> float:
        """
        Simulate one lap and return lap time

        Args:
            lap_number: Current lap number
            race_data: Full race data for context

        Returns:
            AI's lap time for this lap
        """
        self.ai_state.current_lap = lap_number
        self.ai_state.tire_life += 1

        # Predict AI's lap time based on current state
        base_lap_time = self.tire_model.predict_lap_time(
            tire_life=self.ai_state.tire_life,
            compound=self.ai_state.tire_compound,
            lap_number=lap_number,
            position=self.ai_state.current_position
        )

        # Apply strategy adjustments
        # More aggressive = push harder = slight time penalty due to tire wear
        aggression_penalty = (self.strategy_params['aggression'] - 0.5) * 0.1
        lap_time = base_lap_time + aggression_penalty

        # Add realistic variance (driver inconsistency)
        lap_time += np.random.normal(0, 0.05)

        # Accumulate total time
        self.ai_state.total_time += lap_time
        self.ai_state.lap_times.append(lap_time)

        # Log lap
        self._log_event(
            lap=lap_number,
            event_type='lap',
            data={
                'lap_time': lap_time,
                'tire_life': self.ai_state.tire_life,
                'tire_compound': self.ai_state.tire_compound,
                'position': self.ai_state.current_position,
                'cumulative_time': self.ai_state.total_time
            }
        )

        return lap_time

    def make_pit_decision(self, lap_number: int, total_laps: int,
                         race_context: Dict) -> bool:
        """
        Decide whether to pit this lap

        Args:
            lap_number: Current lap number
            total_laps: Total race laps
            race_context: Context about other drivers

        Returns:
            True if AI decides to pit
        """
        # Create race state
        race_state = RaceState(
            current_lap=lap_number,
            total_laps=total_laps,
            current_position=self.ai_state.current_position,
            tire_compound=self.ai_state.tire_compound,
            tire_life=self.ai_state.tire_life,
            gap_ahead=race_context.get('gap_ahead', 2.0),
            gap_behind=race_context.get('gap_behind', 2.0),
            fuel_load=total_laps - lap_number,
            track_status=race_context.get('track_status', '1')
        )

        # Get optimizer decision
        decision = self.optimizer.make_decision(race_state)

        # Apply strategy params to decision
        # More aggressive = pit earlier, more often
        confidence_threshold = 0.7 - (self.strategy_params['aggression'] * 0.3)

        should_pit = decision.should_pit and decision.confidence >= confidence_threshold

        # Log decision
        self._log_event(
            lap=lap_number,
            event_type='pit_decision',
            data={
                'decision': 'PIT' if should_pit else 'STAY_OUT',
                'base_recommendation': decision.should_pit,
                'confidence': decision.confidence,
                'recommended_compound': decision.recommended_compound,
                'reasoning': decision.reasoning,
                'strategy_override': should_pit != decision.should_pit
            }
        )

        # Execute pit stop if decided
        if should_pit:
            self._execute_pit_stop(lap_number, decision.recommended_compound)

        return should_pit

    def _execute_pit_stop(self, lap_number: int, new_compound: str) -> None:
        """Execute a pit stop"""
        old_compound = self.ai_state.tire_compound
        old_tire_life = self.ai_state.tire_life

        # Apply pit stop time penalty
        self.ai_state.total_time += self.optimizer.pit_loss_time

        # Change tires
        self.ai_state.tire_compound = new_compound
        self.ai_state.tire_life = 0

        # Record pit stop
        pit_stop = {
            'lap': lap_number,
            'old_compound': old_compound,
            'new_compound': new_compound,
            'old_tire_life': old_tire_life,
            'time_loss': self.optimizer.pit_loss_time
        }
        self.ai_state.pit_stops.append(pit_stop)

        # Log pit stop
        self._log_event(
            lap=lap_number,
            event_type='pit_stop',
            data=pit_stop
        )

    def update_position(self, new_position: int, lap_number: int) -> None:
        """
        Update AI's position in race

        Args:
            new_position: New race position
            lap_number: Current lap
        """
        old_position = self.ai_state.current_position
        position_change = old_position - new_position  # Positive = gained positions

        self.ai_state.current_position = new_position
        self.ai_state.positions.append(new_position)

        if position_change != 0:
            self._log_event(
                lap=lap_number,
                event_type='position_change',
                data={
                    'old_position': old_position,
                    'new_position': new_position,
                    'positions_gained': position_change
                }
            )

    def _log_event(self, lap: int, event_type: str, data: Dict) -> None:
        """Log a race event"""
        event = RaceEvent(
            lap=lap,
            timestamp=self.ai_state.total_time,
            event_type=event_type,
            driver=self.ai_state.driver_name,
            data=data
        )
        self.race_events.append(event)

    def get_decision_log(self) -> pd.DataFrame:
        """
        Get all decisions made during race

        Returns:
            DataFrame of all pit decisions with reasoning
        """
        decisions = [
            event for event in self.race_events
            if event.event_type == 'pit_decision'
        ]

        if not decisions:
            return pd.DataFrame()

        log_data = []
        for event in decisions:
            log_entry = {
                'Lap': event.lap,
                'Decision': event.data['decision'],
                'Confidence': f"{event.data['confidence']*100:.0f}%",
                'Recommended_Compound': event.data['recommended_compound'],
                'Reasoning': ' | '.join(event.data['reasoning'][:2])  # First 2 reasons
            }
            log_data.append(log_entry)

        return pd.DataFrame(log_data)

    def get_race_summary(self) -> Dict:
        """Get summary of AI's race performance"""
        if not self.ai_state:
            return {}

        return {
            'driver': self.ai_state.driver_name,
            'final_position': self.ai_state.current_position,
            'total_time': self.ai_state.total_time,
            'total_pit_stops': len(self.ai_state.pit_stops),
            'average_lap_time': np.mean(self.ai_state.lap_times) if self.ai_state.lap_times else 0,
            'best_lap_time': np.min(self.ai_state.lap_times) if self.ai_state.lap_times else 0,
            'starting_position': self.ai_state.positions[0] if self.ai_state.positions else 20,
            'positions_gained': (self.ai_state.positions[0] - self.ai_state.current_position) if self.ai_state.positions else 0
        }

    def learn_from_race(self, final_position: int, winner_time: float) -> None:
        """
        Update strategy parameters based on race result

        Args:
            final_position: Final position in race
            winner_time: Winner's total race time
        """
        # Calculate performance metrics
        time_delta = self.ai_state.total_time - winner_time
        position_performance = (20 - final_position) / 20  # 0-1 scale

        # Update strategy based on performance
        lr = self.strategy_params['learning_rate']

        # If finished poorly, adjust aggression
        if final_position > 15:
            # Try being more conservative
            self.strategy_params['aggression'] *= (1 - lr)
        elif final_position < 10:
            # Being aggressive worked, increase it
            self.strategy_params['aggression'] = min(1.0, self.strategy_params['aggression'] * (1 + lr))

        # Store result
        self.race_results_history.append({
            'position': final_position,
            'time_delta': time_delta,
            'pit_stops': len(self.ai_state.pit_stops),
            'strategy_params': self.strategy_params.copy()
        })

        self._log_event(
            lap=self.ai_state.current_lap,
            event_type='race_end',
            data={
                'final_position': final_position,
                'time_delta': time_delta,
                'learned_params': self.strategy_params
            }
        )

    def save_decision_log(self, filepath: str = 'ai_decision_log.json') -> None:
        """Save complete decision log to file"""
        log_data = {
            'race_summary': self.get_race_summary(),
            'strategy_params': self.strategy_params,
            'events': [
                {
                    'lap': event.lap,
                    'timestamp': event.timestamp,
                    'type': event.event_type,
                    'data': event.data
                }
                for event in self.race_events
            ]
        }

        with open(filepath, 'w') as f:
            json.dump(log_data, f, indent=2)

        print(f"✅ Decision log saved to {filepath}")


if __name__ == '__main__':
    print("=" * 60)
    print("AI RACING AGENT - Test")
    print("=" * 60)

    # Load models
    from data_processor import F1DataProcessor

    processor = F1DataProcessor(2024, 'Monaco')
    processor.load_race_data()
    lap_data = processor.extract_lap_features()

    tire_model = TireDegradationModel()
    tire_model.train(lap_data)

    optimizer = PitStopOptimizer(tire_model)

    # Create AI agent
    ai = RacingAI(tire_model, optimizer, strategy_params={
        'aggression': 0.8,
        'risk_tolerance': 0.6,
        'tire_preference': 'MEDIUM'
    })

    # Test race simulation
    total_laps = 78
    ai.initialize_race('Monaco', total_laps, starting_position=20)

    print(f"\n🏁 AI Starting Position: P{ai.ai_state.current_position}")
    print(f"Starting Tire: {ai.ai_state.tire_compound}")

    # Simulate first 30 laps
    for lap in range(1, 31):
        # Simulate lap
        lap_time = ai.simulate_lap(lap, lap_data)

        # Make pit decision every lap
        race_context = {
            'gap_ahead': 2.5,
            'gap_behind': 3.0,
            'track_status': '1'
        }

        pitted = ai.make_pit_decision(lap, total_laps, race_context)

        if pitted:
            print(f"\nLap {lap}: 🔧 PIT STOP - {ai.ai_state.tire_compound}")

    print(f"\n📊 After 30 laps:")
    print(f"Total time: {ai.ai_state.total_time:.2f}s")
    print(f"Pit stops: {len(ai.ai_state.pit_stops)}")
    print(f"Current tire: {ai.ai_state.tire_compound} ({ai.ai_state.tire_life} laps old)")

    # Get decision log
    print("\n📋 DECISION LOG:")
    decision_log = ai.get_decision_log()
    print(decision_log.head(10))

    # Save log
    ai.save_decision_log('test_ai_log.json')

    print("\n✅ AI Racing Agent ready!")
