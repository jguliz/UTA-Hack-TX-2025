"""
Pit Stop Strategy Optimizer
Real-time decision engine for optimal pit stop timing
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from tire_model import TireDegradationModel
from data_processor import F1DataProcessor
from dataclasses import dataclass


@dataclass
class RaceState:
    """Current race state for decision making"""
    current_lap: int
    total_laps: int
    current_position: int
    tire_compound: str
    tire_life: int  # Laps on current tire
    gap_ahead: float  # Seconds to car ahead
    gap_behind: float  # Seconds to car behind
    fuel_load: float  # Approximated by laps remaining
    track_status: str  # '1' = green, '2' = yellow, '4' = safety car
    air_temp: float = 25.0
    track_temp: float = 35.0
    rainfall: bool = False


@dataclass
class PitDecision:
    """Pit stop decision with reasoning"""
    should_pit: bool
    confidence: float  # 0-1
    expected_position_change: int  # Negative = lose positions, positive = gain
    expected_time_delta: float  # Seconds gained/lost
    recommended_compound: str
    reasoning: List[str]
    alternative_lap: Optional[int] = None  # Alternative pit window


class PitStopOptimizer:
    """AI-powered pit stop strategy optimizer"""

    def __init__(self, tire_model: TireDegradationModel, pit_loss_time: float = 24.0):
        """
        Initialize optimizer

        Args:
            tire_model: Trained tire degradation model
            pit_loss_time: Typical time lost in pit stop (seconds)
        """
        self.tire_model = tire_model
        self.pit_loss_time = pit_loss_time
        self.compound_ranking = {
            'SOFT': {'speed': 1.0, 'durability': 0.6},
            'MEDIUM': {'speed': 0.8, 'durability': 0.8},
            'HARD': {'speed': 0.6, 'durability': 1.0}
        }

    def calculate_undercut_advantage(self, race_state: RaceState,
                                     opponent_tire_life: int) -> float:
        """
        Calculate undercut advantage (pitting earlier than opponent)

        Args:
            race_state: Current race state
            opponent_tire_life: Opponent's tire age

        Returns:
            Expected time gain in seconds (positive = advantage)
        """
        # Fresh tire advantage
        my_fresh_time = self.tire_model.predict_lap_time(
            tire_life=1,
            compound=race_state.tire_compound,
            lap_number=race_state.current_lap,
            position=race_state.current_position
        )

        # Opponent on old tires
        opponent_old_time = self.tire_model.predict_lap_time(
            tire_life=opponent_tire_life,
            compound=race_state.tire_compound,
            lap_number=race_state.current_lap,
            position=race_state.current_position - 1  # Car ahead
        )

        # Undercut advantage = (opponent lap time - my lap time after pit) - pit loss
        undercut_advantage = (opponent_old_time - my_fresh_time) - (self.pit_loss_time / 10)

        return undercut_advantage

    def calculate_overcut_advantage(self, race_state: RaceState,
                                    laps_to_extend: int) -> float:
        """
        Calculate overcut advantage (staying out longer)

        Args:
            race_state: Current race state
            laps_to_extend: Additional laps to stay out

        Returns:
            Expected time gain in seconds
        """
        # Track position advantage from staying out
        time_on_old_tires = 0
        for lap in range(laps_to_extend):
            tire_life = race_state.tire_life + lap + 1
            lap_time = self.tire_model.predict_lap_time(
                tire_life=tire_life,
                compound=race_state.tire_compound,
                lap_number=race_state.current_lap + lap,
                position=race_state.current_position
            )
            time_on_old_tires += lap_time

        # Opponent pits now, fresh tires
        opponent_fresh_time = self.tire_model.predict_lap_time(
            tire_life=1,
            compound=race_state.tire_compound,
            lap_number=race_state.current_lap,
            position=race_state.current_position + 1
        ) * laps_to_extend

        # Overcut works if staying out on old tires < opponent on fresh + pit loss
        overcut_advantage = (opponent_fresh_time + self.pit_loss_time) - time_on_old_tires

        return overcut_advantage

    def simulate_race_to_end(self, race_state: RaceState, pit_lap: int,
                            new_compound: str) -> float:
        """
        Monte Carlo simulation of race from current lap to finish

        Args:
            race_state: Current race state
            pit_lap: Lap to pit on
            new_compound: Compound to switch to

        Returns:
            Total time to finish race
        """
        total_time = 0
        current_tire_life = race_state.tire_life
        current_compound = race_state.tire_compound

        for lap in range(race_state.current_lap, race_state.total_laps + 1):
            # Pit stop
            if lap == pit_lap:
                total_time += self.pit_loss_time
                current_compound = new_compound
                current_tire_life = 0

            # Lap time
            current_tire_life += 1
            lap_time = self.tire_model.predict_lap_time(
                tire_life=current_tire_life,
                compound=current_compound,
                lap_number=lap,
                position=race_state.current_position,
                air_temp=race_state.air_temp,
                track_temp=race_state.track_temp,
                rainfall=race_state.rainfall
            )

            total_time += lap_time

        return total_time

    def find_optimal_pit_window(self, race_state: RaceState,
                               compounds: List[str] = None) -> Dict:
        """
        Find optimal pit window using dynamic programming

        Args:
            race_state: Current race state
            compounds: Compounds to consider (None = all)

        Returns:
            Dictionary with optimal pit lap, compound, and expected time
        """
        if compounds is None:
            compounds = ['SOFT', 'MEDIUM', 'HARD']

        # Search window: next 3-15 laps
        search_window = range(
            race_state.current_lap + 3,
            min(race_state.current_lap + 20, race_state.total_laps - 5)
        )

        best_strategy = {
            'pit_lap': None,
            'compound': None,
            'total_time': float('inf'),
            'time_saved': 0
        }

        # Baseline: no pit stop (if already pitted)
        if race_state.tire_life > 0:
            baseline_time = self.simulate_race_to_end(
                race_state,
                pit_lap=race_state.total_laps + 1,  # Don't pit
                new_compound=race_state.tire_compound
            )
        else:
            baseline_time = float('inf')

        # Try different pit windows
        for pit_lap in search_window:
            for compound in compounds:
                # Skip if same compound and already fresh tires
                if compound == race_state.tire_compound and race_state.tire_life < 5:
                    continue

                total_time = self.simulate_race_to_end(race_state, pit_lap, compound)

                if total_time < best_strategy['total_time']:
                    best_strategy = {
                        'pit_lap': pit_lap,
                        'compound': compound,
                        'total_time': total_time,
                        'time_saved': baseline_time - total_time
                    }

        return best_strategy

    def make_decision(self, race_state: RaceState) -> PitDecision:
        """
        Make real-time pit stop decision

        Args:
            race_state: Current race state

        Returns:
            PitDecision object with recommendation
        """
        reasoning = []

        # Safety car override
        if race_state.track_status in ['2', '4']:
            reasoning.append("🟡 Safety car/yellow flag - FREE PIT STOP OPPORTUNITY")
            return PitDecision(
                should_pit=True,
                confidence=0.95,
                expected_position_change=0,
                expected_time_delta=-15.0,  # Minimal time loss
                recommended_compound='MEDIUM',
                reasoning=reasoning
            )

        # Find optimal strategy
        optimal = self.find_optimal_pit_window(race_state)

        # Decision logic
        laps_until_optimal = optimal['pit_lap'] - race_state.current_lap if optimal['pit_lap'] else 999

        # Should pit now?
        should_pit_now = False
        confidence = 0.0

        if laps_until_optimal <= 2:
            should_pit_now = True
            confidence = 0.9
            reasoning.append(f"✅ Optimal pit window (lap {optimal['pit_lap']})")
            reasoning.append(f"💰 Expected to save {optimal['time_saved']:.2f}s")

        # Tire degradation critical
        elif race_state.tire_life > 25:
            current_pace = self.tire_model.predict_lap_time(
                tire_life=race_state.tire_life,
                compound=race_state.tire_compound,
                lap_number=race_state.current_lap,
                position=race_state.current_position
            )
            fresh_pace = self.tire_model.predict_lap_time(
                tire_life=1,
                compound=race_state.tire_compound,
                lap_number=race_state.current_lap,
                position=race_state.current_position
            )

            if current_pace - fresh_pace > 1.5:
                should_pit_now = True
                confidence = 0.8
                reasoning.append(f"⚠️  Critical tire degradation (+{current_pace - fresh_pace:.2f}s/lap)")

        # Undercut opportunity
        elif race_state.gap_ahead < 2.5 and race_state.tire_life > 10:
            undercut_adv = self.calculate_undercut_advantage(race_state, race_state.tire_life + 5)
            if undercut_adv > 0.3:
                should_pit_now = True
                confidence = 0.75
                reasoning.append(f"🎯 Undercut opportunity (+{undercut_adv:.2f}s advantage)")

        # Stay out
        else:
            reasoning.append(f"🏁 Stay out - optimal window in {laps_until_optimal} laps")
            reasoning.append(f"📊 Current tire life: {race_state.tire_life} laps")

        # Position change estimation
        expected_position_change = 0
        if should_pit_now:
            # Estimate positions lost during pit (cars within pit loss time)
            expected_position_change = -int(race_state.gap_behind / self.pit_loss_time)

        return PitDecision(
            should_pit=should_pit_now,
            confidence=confidence,
            expected_position_change=expected_position_change,
            expected_time_delta=optimal['time_saved'] if should_pit_now else 0,
            recommended_compound=optimal['compound'] if optimal['compound'] else 'MEDIUM',
            reasoning=reasoning,
            alternative_lap=optimal['pit_lap'] if not should_pit_now else None
        )

    def backtest_race(self, race_data: pd.DataFrame, driver: str) -> Dict:
        """
        Backtest optimizer on historical race

        Args:
            race_data: Full race lap data
            driver: Driver to analyze

        Returns:
            Backtest results with AI vs actual comparison
        """
        driver_laps = race_data[race_data['Driver'] == driver].sort_values('LapNumber')

        if len(driver_laps) == 0:
            return {'error': f'No data for driver {driver}'}

        total_laps = driver_laps['LapNumber'].max()
        actual_pit_laps = driver_laps[driver_laps['Stint'] != driver_laps['Stint'].shift(1)]['LapNumber'].tolist()[1:]

        ai_decisions = []

        # Simulate race lap by lap
        for _, lap in driver_laps.iterrows():
            race_state = RaceState(
                current_lap=int(lap['LapNumber']),
                total_laps=int(total_laps),
                current_position=int(lap['Position']) if pd.notna(lap['Position']) else 10,
                tire_compound=lap['Compound'] if pd.notna(lap['Compound']) else 'MEDIUM',
                tire_life=int(lap['TyreLife']) if pd.notna(lap['TyreLife']) else 1,
                gap_ahead=1.5,  # Simplified
                gap_behind=1.5,
                fuel_load=total_laps - lap['LapNumber'],
                track_status='1'
            )

            decision = self.make_decision(race_state)

            if decision.should_pit:
                ai_decisions.append({
                    'lap': race_state.current_lap,
                    'confidence': decision.confidence,
                    'compound': decision.recommended_compound,
                    'reasoning': ' | '.join(decision.reasoning)
                })

        return {
            'driver': driver,
            'actual_pit_laps': actual_pit_laps,
            'ai_pit_recommendations': ai_decisions,
            'agreement_rate': len(set([d['lap'] for d in ai_decisions]) & set(actual_pit_laps)) / max(len(actual_pit_laps), 1)
        }


if __name__ == '__main__':
    print("=" * 60)
    print("PIT STOP OPTIMIZER - Example Usage")
    print("=" * 60)

    # Load tire model
    print("\n📦 Loading tire degradation model...")
    tire_model = TireDegradationModel()

    # Train on Monaco 2024
    processor = F1DataProcessor(2024, 'Monaco')
    processor.load_race_data()
    lap_data = processor.extract_lap_features()
    tire_model.train(lap_data)

    # Initialize optimizer
    optimizer = PitStopOptimizer(tire_model, pit_loss_time=24.0)

    # Example decision
    print("\n🏎️  REAL-TIME DECISION EXAMPLE:")
    print("-" * 60)

    example_state = RaceState(
        current_lap=25,
        total_laps=78,
        current_position=5,
        tire_compound='MEDIUM',
        tire_life=18,
        gap_ahead=2.1,
        gap_behind=3.5,
        fuel_load=53,
        track_status='1'
    )

    decision = optimizer.make_decision(example_state)

    print(f"Lap {example_state.current_lap}/{example_state.total_laps}")
    print(f"Position: P{example_state.current_position}")
    print(f"Current tire: {example_state.tire_compound} ({example_state.tire_life} laps old)")
    print(f"\n{'PIT NOW' if decision.should_pit else 'STAY OUT'} (Confidence: {decision.confidence*100:.0f}%)")
    print(f"Recommended compound: {decision.recommended_compound}")
    if decision.expected_position_change != 0:
        print(f"Expected position change: {decision.expected_position_change:+d}")
    if decision.alternative_lap:
        print(f"Alternative window: Lap {decision.alternative_lap}")
    print("\nReasoning:")
    for reason in decision.reasoning:
        print(f"  {reason}")

    # Backtest
    print("\n" + "=" * 60)
    print("BACKTESTING ON MONACO 2024")
    print("=" * 60)

    drivers_to_test = ['VER', 'LEC', 'NOR']

    for driver in drivers_to_test:
        print(f"\n🏁 {driver}:")
        result = optimizer.backtest_race(lap_data, driver)

        if 'error' in result:
            print(f"  ❌ {result['error']}")
            continue

        print(f"  Actual pit stops: Laps {result['actual_pit_laps']}")
        print(f"  AI recommendations: {len(result['ai_pit_recommendations'])} pit windows")
        for rec in result['ai_pit_recommendations'][:3]:  # Show first 3
            print(f"    Lap {rec['lap']} ({rec['confidence']*100:.0f}%): {rec['compound']}")

    print("\n✅ Pit stop optimizer ready!")
    print("Next steps:")
    print("  1. Backtest on multiple 2024 races")
    print("  2. Compare AI strategy vs actual results")
    print("  3. Build demo dashboard")
