"""
Data Preprocessing Pipeline for F1 Strategy Optimization
Extracts and engineers features from FastF1 for ML models
"""

import fastf1
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import os

# Enable caching
cache_dir = 'fastf1_cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
fastf1.Cache.enable_cache(cache_dir)


class F1DataProcessor:
    """Process F1 race data into features for strategy optimization"""

    def __init__(self, year: int, race_name: str):
        """
        Initialize processor for a specific race

        Args:
            year: Race year (e.g., 2024)
            race_name: Race name (e.g., 'Monaco', 'Spa', 'Silverstone')
        """
        self.year = year
        self.race_name = race_name
        self.session = None
        self.laps = None
        self.weather = None

    def load_race_data(self) -> None:
        """Load race session data from FastF1"""
        print(f"Loading {self.year} {self.race_name} GP data...")
        self.session = fastf1.get_session(self.year, self.race_name, 'R')
        self.session.load()
        self.laps = self.session.laps
        self.weather = self.session.weather_data
        print(f"✅ Loaded {len(self.laps)} laps")

    def extract_lap_features(self) -> pd.DataFrame:
        """
        Extract lap-level features for tire degradation modeling

        Returns:
            DataFrame with features: driver, lap_number, lap_time, tire_compound,
            tire_life, track_status, air_temp, track_temp, position
        """
        if self.laps is None:
            raise ValueError("Must call load_race_data() first")

        # Select relevant columns
        features = self.laps[[
            'Driver', 'LapNumber', 'LapTime', 'Compound', 'TyreLife',
            'TrackStatus', 'Position', 'Stint', 'Team'
        ]].copy()

        # Convert lap time to seconds (float)
        features['LapTimeSeconds'] = features['LapTime'].dt.total_seconds()

        # Add weather data (merge on time)
        if self.weather is not None and not self.weather.empty:
            # Get average weather per lap
            weather_summary = self.weather.groupby(
                self.weather['Time'].dt.floor('60s')
            ).agg({
                'AirTemp': 'mean',
                'TrackTemp': 'mean',
                'Humidity': 'mean',
                'Rainfall': 'max'
            }).reset_index()

            # For simplicity, use median weather across race
            features['AirTemp'] = self.weather['AirTemp'].median()
            features['TrackTemp'] = self.weather['TrackTemp'].median()
            features['Rainfall'] = self.weather['Rainfall'].max()

        # Remove outlier laps (pit laps, safety car, etc.)
        features = features[
            (features['TrackStatus'] == '1') &  # Green flag only
            (features['LapTimeSeconds'].notna()) &
            (features['TyreLife'].notna()) &
            (features['TyreLife'] > 0)
        ]

        return features

    def extract_pit_stop_data(self) -> pd.DataFrame:
        """
        Extract pit stop decisions with context

        Returns:
            DataFrame with: driver, lap_pitted, tire_before, tire_after,
            laps_on_tire, position_before, gap_ahead, gap_behind
        """
        if self.laps is None:
            raise ValueError("Must call load_race_data() first")

        pit_stops = []

        for driver in self.laps['Driver'].unique():
            driver_laps = self.laps[self.laps['Driver'] == driver].sort_values('LapNumber')

            # Find pit stops (stint changes)
            stint_changes = driver_laps[driver_laps['Stint'] != driver_laps['Stint'].shift(1)]

            for idx in stint_changes.index[1:]:  # Skip first stint
                pit_lap = driver_laps.loc[idx, 'LapNumber']
                prev_lap_idx = driver_laps[driver_laps['LapNumber'] == pit_lap - 1].index

                if len(prev_lap_idx) == 0:
                    continue

                prev_lap_idx = prev_lap_idx[0]

                pit_stop = {
                    'Driver': driver,
                    'LapPitted': pit_lap,
                    'TireBefore': driver_laps.loc[prev_lap_idx, 'Compound'],
                    'TireAfter': driver_laps.loc[idx, 'Compound'],
                    'LapsOnTire': driver_laps.loc[prev_lap_idx, 'TyreLife'],
                    'PositionBefore': driver_laps.loc[prev_lap_idx, 'Position'],
                    'PositionAfter': driver_laps.loc[idx, 'Position'],
                    'Team': driver_laps.loc[idx, 'Team']
                }

                pit_stops.append(pit_stop)

        return pd.DataFrame(pit_stops)

    def calculate_tire_degradation(self, driver: str = None) -> pd.DataFrame:
        """
        Calculate tire degradation rate for each compound

        Args:
            driver: Specific driver to analyze (None = all drivers)

        Returns:
            DataFrame with degradation stats per compound
        """
        features = self.extract_lap_features()

        if driver:
            features = features[features['Driver'] == driver]

        # Group by compound and tire life
        degradation = features.groupby(['Compound', 'TyreLife']).agg({
            'LapTimeSeconds': ['mean', 'std', 'count']
        }).reset_index()

        degradation.columns = ['Compound', 'TyreLife', 'AvgLapTime', 'StdLapTime', 'SampleSize']

        # Calculate degradation rate (seconds lost per lap)
        for compound in degradation['Compound'].unique():
            compound_data = degradation[degradation['Compound'] == compound].copy()

            if len(compound_data) > 5:
                # Linear regression: lap time vs tire life
                from scipy import stats
                slope, intercept, r_value, p_value, std_err = stats.linregress(
                    compound_data['TyreLife'],
                    compound_data['AvgLapTime']
                )

                degradation.loc[degradation['Compound'] == compound, 'DegradationRate'] = slope
                degradation.loc[degradation['Compound'] == compound, 'R_squared'] = r_value**2

        return degradation

    def get_race_summary(self) -> Dict:
        """Get high-level race statistics"""
        if self.laps is None:
            raise ValueError("Must call load_race_data() first")

        pit_stops = self.extract_pit_stop_data()

        summary = {
            'race': f"{self.year} {self.race_name}",
            'total_laps': self.laps['LapNumber'].max(),
            'num_drivers': self.laps['Driver'].nunique(),
            'total_pit_stops': len(pit_stops),
            'compounds_used': self.laps['Compound'].dropna().unique().tolist(),
            'winner': self.laps[self.laps['Position'] == 1]['Driver'].iloc[0] if len(self.laps[self.laps['Position'] == 1]) > 0 else 'Unknown'
        }

        return summary


def process_multiple_races(year: int, race_names: List[str]) -> pd.DataFrame:
    """
    Process multiple races and combine into single dataset

    Args:
        year: Season year
        race_names: List of race names

    Returns:
        Combined DataFrame of all lap features
    """
    all_laps = []

    for race_name in race_names:
        try:
            processor = F1DataProcessor(year, race_name)
            processor.load_race_data()

            laps = processor.extract_lap_features()
            laps['RaceName'] = race_name

            all_laps.append(laps)
            print(f"✅ Processed {race_name}")

        except Exception as e:
            print(f"⚠️  Failed to process {race_name}: {str(e)}")
            continue

    return pd.concat(all_laps, ignore_index=True)


if __name__ == '__main__':
    # Example usage
    print("=" * 60)
    print("F1 DATA PROCESSOR - Example Usage")
    print("=" * 60)

    # Process Monaco 2024
    processor = F1DataProcessor(2024, 'Monaco')
    processor.load_race_data()

    # Get race summary
    summary = processor.get_race_summary()
    print("\n📊 RACE SUMMARY:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    # Extract lap features
    print("\n📈 EXTRACTING LAP FEATURES...")
    lap_features = processor.extract_lap_features()
    print(f"  Total valid laps: {len(lap_features)}")
    print(f"\nSample features:")
    print(lap_features[['Driver', 'LapNumber', 'LapTimeSeconds', 'Compound', 'TyreLife', 'Position']].head(10))

    # Extract pit stops
    print("\n🔧 PIT STOP ANALYSIS:")
    pit_stops = processor.extract_pit_stop_data()
    print(f"  Total pit stops: {len(pit_stops)}")
    print(f"\nSample pit stops:")
    print(pit_stops[['Driver', 'LapPitted', 'TireBefore', 'TireAfter', 'LapsOnTire', 'PositionBefore', 'PositionAfter']].head(10))

    # Tire degradation
    print("\n🏎️  TIRE DEGRADATION ANALYSIS:")
    degradation = processor.calculate_tire_degradation()
    print(degradation)

    print("\n✅ Data preprocessing pipeline ready!")
    print("Next steps:")
    print("  1. Train tire degradation model")
    print("  2. Build pit stop optimizer")
    print("  3. Backtest on multiple races")
