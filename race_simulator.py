"""
Race Simulator - AI vs Real F1 Drivers
Simulates full race with AI competing for position
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from racing_agent import RacingAI
from tire_model import TireDegradationModel
from pit_optimizer import PitStopOptimizer
from data_processor import F1DataProcessor


class RaceSimulator:
    """Simulate AI racing against real F1 drivers"""

    def __init__(self, processor: F1DataProcessor, ai_agent: RacingAI):
        """
        Initialize race simulator

        Args:
            processor: F1 data processor with loaded race
            ai_agent: AI racing agent
        """
        self.processor = processor
        self.ai = ai_agent
        # Use processed lap features instead of raw laps
        self.race_data = processor.extract_lap_features()
        self.total_laps = int(self.race_data['LapNumber'].max())

        # Build driver standings by lap
        self.driver_standings = self._build_standings_by_lap()

    def _build_standings_by_lap(self) -> Dict[int, pd.DataFrame]:
        """
        Build standings for each lap

        Returns:
            Dict mapping lap number to standings DataFrame
        """
        standings = {}

        for lap in range(1, self.total_laps + 1):
            lap_data = self.race_data[self.race_data['LapNumber'] == lap].copy()

            if len(lap_data) == 0:
                continue

            # Get cumulative time for each driver
            driver_times = []

            for driver in lap_data['Driver'].unique():
                driver_laps = self.race_data[
                    (self.race_data['Driver'] == driver) &
                    (self.race_data['LapNumber'] <= lap)
                ].copy()

                if len(driver_laps) > 0:
                    # Sum lap times up to this lap
                    total_time = driver_laps['LapTimeSeconds'].sum()

                    # Get current tire info
                    current_lap_data = driver_laps[driver_laps['LapNumber'] == lap].iloc[-1]

                    driver_times.append({
                        'Driver': driver,
                        'Team': current_lap_data['Team'],
                        'TotalTime': total_time,
                        'CurrentLap': lap,
                        'Compound': current_lap_data['Compound'],
                        'TyreLife': current_lap_data['TyreLife'],
                        'Stint': current_lap_data['Stint']
                    })

            if driver_times:
                standings_df = pd.DataFrame(driver_times)
                standings_df = standings_df.sort_values('TotalTime')
                standings_df['Position'] = range(1, len(standings_df) + 1)

                standings[lap] = standings_df

        return standings

    def simulate_full_race(self, starting_position: int = 20,
                          starting_compound: str = "MEDIUM") -> pd.DataFrame:
        """
        Simulate full race with AI

        Args:
            starting_position: AI's starting grid position
            starting_compound: AI's starting tire compound

        Returns:
            DataFrame with lap-by-lap standings including AI
        """
        print("=" * 60)
        print(f"🏁 RACE SIMULATION: {self.processor.race_name} GP")
        print("=" * 60)

        # Initialize AI
        self.ai.initialize_race(
            self.processor.race_name,
            self.total_laps,
            starting_position,
            starting_compound
        )

        print(f"\n🤖 AI Driver: {self.ai.ai_state.driver_name}")
        print(f"Starting Position: P{starting_position}")
        print(f"Starting Tire: {starting_compound}")
        print(f"Strategy Params: Aggression={self.ai.strategy_params['aggression']:.2f}")

        all_standings = []

        # Simulate each lap
        for lap in range(1, self.total_laps + 1):
            # Get real driver standings for this lap
            if lap not in self.driver_standings:
                continue

            real_standings = self.driver_standings[lap].copy()

            # AI simulates this lap
            ai_lap_time = self.ai.simulate_lap(lap, self.race_data)

            # Determine AI position based on cumulative time
            ai_total_time = self.ai.ai_state.total_time

            # Insert AI into standings
            ai_row = {
                'Driver': self.ai.ai_state.driver_name,
                'Team': self.ai.ai_state.team,
                'TotalTime': ai_total_time,
                'CurrentLap': lap,
                'Compound': self.ai.ai_state.tire_compound,
                'TyreLife': self.ai.ai_state.tire_life,
                'Stint': len(self.ai.ai_state.pit_stops) + 1,
                'IsAI': True
            }

            real_standings['IsAI'] = False
            combined = pd.concat([real_standings, pd.DataFrame([ai_row])], ignore_index=True)
            combined = combined.sort_values('TotalTime').reset_index(drop=True)
            combined['Position'] = range(1, len(combined) + 1)

            # Update AI position
            ai_position = int(combined[combined['Driver'] == self.ai.ai_state.driver_name]['Position'].iloc[0])
            self.ai.update_position(ai_position, lap)

            # Store standings
            combined['Lap'] = lap
            all_standings.append(combined)

            # AI makes pit decision
            race_context = self._get_race_context(combined, lap)
            pitted = self.ai.make_pit_decision(lap, self.total_laps, race_context)

            # Print progress
            if lap % 10 == 0 or pitted:
                position_str = f"P{ai_position}"
                tire_str = f"{self.ai.ai_state.tire_compound}({self.ai.ai_state.tire_life})"
                pit_str = "🔧 PITTED" if pitted else ""

                print(f"Lap {lap:2d}/{self.total_laps}: {position_str:4s} | {tire_str:12s} | {ai_lap_time:5.2f}s {pit_str}")

        # Combine all standings
        full_standings = pd.concat(all_standings, ignore_index=True)

        # Race summary
        print("\n" + "=" * 60)
        print("🏁 RACE COMPLETE")
        print("=" * 60)

        summary = self.ai.get_race_summary()
        print(f"\n🤖 AI Performance:")
        print(f"  Final Position: P{summary['final_position']}")
        print(f"  Starting Position: P{summary['starting_position']}")
        print(f"  Positions Gained: {summary['positions_gained']:+d}")
        print(f"  Total Pit Stops: {summary['total_pit_stops']}")
        print(f"  Average Lap Time: {summary['average_lap_time']:.3f}s")
        print(f"  Best Lap: {summary['best_lap_time']:.3f}s")

        # Compare to winner
        final_standings = full_standings[full_standings['Lap'] == self.total_laps].sort_values('Position')
        winner = final_standings.iloc[0]
        ai_final = final_standings[final_standings['Driver'] == self.ai.ai_state.driver_name].iloc[0]

        time_delta = ai_final['TotalTime'] - winner['TotalTime']
        print(f"\n🏆 Race Winner: {winner['Driver']} ({winner['TotalTime']:.2f}s)")
        print(f"  AI Time Delta: +{time_delta:.2f}s")

        # Learn from race
        self.ai.learn_from_race(summary['final_position'], winner['TotalTime'])

        return full_standings

    def _get_race_context(self, standings: pd.DataFrame, lap: int) -> Dict:
        """Get race context for AI decision making"""
        ai_position = standings[standings['Driver'] == self.ai.ai_state.driver_name]['Position'].iloc[0]

        # Get gap to car ahead
        if ai_position > 1:
            car_ahead = standings[standings['Position'] == ai_position - 1].iloc[0]
            gap_ahead = abs(car_ahead['TotalTime'] - self.ai.ai_state.total_time)
        else:
            gap_ahead = 0

        # Get gap to car behind
        if ai_position < len(standings):
            car_behind = standings[standings['Position'] == ai_position + 1].iloc[0]
            gap_behind = abs(self.ai.ai_state.total_time - car_behind['TotalTime'])
        else:
            gap_behind = 999

        return {
            'gap_ahead': gap_ahead,
            'gap_behind': gap_behind,
            'track_status': '1'  # Simplified, could add safety car detection
        }

    def get_final_classification(self, full_standings: pd.DataFrame) -> pd.DataFrame:
        """
        Get final race classification

        Args:
            full_standings: Full standings from simulate_full_race

        Returns:
            Final classification table
        """
        final_lap = full_standings['Lap'].max()
        final = full_standings[full_standings['Lap'] == final_lap].copy()
        final = final.sort_values('Position')

        classification = final[[
            'Position', 'Driver', 'Team', 'TotalTime', 'Stint', 'IsAI'
        ]].copy()

        # Add time delta to winner
        winner_time = classification.iloc[0]['TotalTime']
        classification['TimeDelta'] = classification['TotalTime'] - winner_time
        classification['TimeDeltaStr'] = classification['TimeDelta'].apply(
            lambda x: f"+{x:.2f}s" if x > 0 else "Winner"
        )

        return classification

    def get_ai_overtakes(self, full_standings: pd.DataFrame) -> List[Dict]:
        """
        Find all overtakes made by AI

        Args:
            full_standings: Full standings from simulate_full_race

        Returns:
            List of overtake events
        """
        ai_standings = full_standings[full_standings['Driver'] == self.ai.ai_state.driver_name].copy()
        ai_standings = ai_standings.sort_values('Lap')

        overtakes = []

        for i in range(1, len(ai_standings)):
            prev_pos = ai_standings.iloc[i-1]['Position']
            curr_pos = ai_standings.iloc[i]['Position']

            if curr_pos < prev_pos:
                # AI gained positions
                lap = ai_standings.iloc[i]['Lap']

                # Find who was overtaken
                prev_lap_standings = full_standings[full_standings['Lap'] == lap - 1]
                overtaken_drivers = prev_lap_standings[
                    (prev_lap_standings['Position'] >= curr_pos) &
                    (prev_lap_standings['Position'] < prev_pos) &
                    (prev_lap_standings['Driver'] != self.ai.ai_state.driver_name)
                ]['Driver'].tolist()

                overtakes.append({
                    'lap': int(lap),
                    'from_position': int(prev_pos),
                    'to_position': int(curr_pos),
                    'overtaken': overtaken_drivers
                })

        return overtakes


def train_ai_multiple_races(races: List[str], year: int = 2024,
                            num_epochs: int = 3) -> RacingAI:
    """
    Train AI across multiple races

    Args:
        races: List of race names
        year: Season year
        num_epochs: Number of training epochs

    Returns:
        Trained AI agent
    """
    print("=" * 60)
    print("🎓 TRAINING AI ACROSS MULTIPLE RACES")
    print("=" * 60)

    # Load initial race for tire model
    processor = F1DataProcessor(year, races[0])
    processor.load_race_data()
    lap_data = processor.extract_lap_features()

    tire_model = TireDegradationModel()
    tire_model.train(lap_data)

    optimizer = PitStopOptimizer(tire_model)

    # Create AI
    ai = RacingAI(tire_model, optimizer)

    results_summary = []

    for epoch in range(num_epochs):
        print(f"\n{'='*60}")
        print(f"EPOCH {epoch + 1}/{num_epochs}")
        print(f"{'='*60}")

        for race_name in races:
            try:
                # Load race
                processor = F1DataProcessor(year, race_name)
                processor.load_race_data()

                # Simulate race
                simulator = RaceSimulator(processor, ai)
                standings = simulator.simulate_full_race(starting_position=20)

                # Get result
                summary = ai.get_race_summary()
                results_summary.append({
                    'epoch': epoch + 1,
                    'race': race_name,
                    'final_position': summary['final_position'],
                    'positions_gained': summary['positions_gained'],
                    'aggression': ai.strategy_params['aggression']
                })

                print(f"\n✅ {race_name}: P{summary['final_position']} ({summary['positions_gained']:+d})")

            except Exception as e:
                print(f"\n⚠️  Skipping {race_name}: {str(e)}")
                continue

    # Print training summary
    print("\n" + "=" * 60)
    print("📊 TRAINING SUMMARY")
    print("=" * 60)

    results_df = pd.DataFrame(results_summary)

    if len(results_df) > 0 and 'race' in results_df.columns:
        print(results_df.groupby('race').agg({
            'final_position': 'mean',
            'positions_gained': 'sum'
        }).round(1))
    else:
        print("No training results to summarize")

    return ai


if __name__ == '__main__':
    # Test race simulation
    processor = F1DataProcessor(2024, 'Monaco')
    processor.load_race_data()
    lap_data = processor.extract_lap_features()

    tire_model = TireDegradationModel()
    tire_model.train(lap_data)

    optimizer = PitStopOptimizer(tire_model)
    ai = RacingAI(tire_model, optimizer, strategy_params={
        'aggression': 0.75,
        'risk_tolerance': 0.6
    })

    simulator = RaceSimulator(processor, ai)
    standings = simulator.simulate_full_race(starting_position=15, starting_compound='MEDIUM')

    # Final classification
    print("\n📊 FINAL CLASSIFICATION:")
    final = simulator.get_final_classification(standings)
    print(final.head(10))

    # AI overtakes
    overtakes = simulator.get_ai_overtakes(standings)
    print(f"\n🎯 AI Overtakes: {len(overtakes)}")
    for overtake in overtakes[:5]:
        print(f"  Lap {overtake['lap']}: P{overtake['from_position']} → P{overtake['to_position']}")

    # Save decision log
    ai.save_decision_log(f'ai_monaco_{ai.get_race_summary()["final_position"]}.json')
