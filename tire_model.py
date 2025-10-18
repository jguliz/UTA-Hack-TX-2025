"""
Tire Degradation Model
Predicts lap time based on tire compound, tire age, and track conditions
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
from typing import Dict, Tuple
import matplotlib.pyplot as plt


class TireDegradationModel:
    """ML model to predict lap times based on tire degradation"""

    def __init__(self, model_type: str = 'gradient_boost'):
        """
        Initialize tire degradation model

        Args:
            model_type: 'gradient_boost', 'random_forest', or 'ridge'
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.compound_encoder = LabelEncoder()
        self.driver_encoder = LabelEncoder()
        self.team_encoder = LabelEncoder()
        self.feature_names = []
        self.is_fitted = False

        # Initialize model
        if model_type == 'gradient_boost':
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=4,
                random_state=42
            )
        elif model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
        elif model_type == 'ridge':
            self.model = Ridge(alpha=1.0)
        else:
            raise ValueError(f"Unknown model_type: {model_type}")

    def prepare_features(self, data: pd.DataFrame, fit_encoders: bool = False) -> np.ndarray:
        """
        Prepare features for training/prediction

        Args:
            data: DataFrame with lap data
            fit_encoders: Whether to fit encoders (True for training, False for prediction)

        Returns:
            Feature matrix
        """
        df = data.copy()

        # Handle categorical encoding
        if fit_encoders:
            df['CompoundEncoded'] = self.compound_encoder.fit_transform(df['Compound'].fillna('UNKNOWN'))
            df['DriverEncoded'] = self.driver_encoder.fit_transform(df['Driver'].fillna('UNKNOWN'))
            df['TeamEncoded'] = self.team_encoder.fit_transform(df['Team'].fillna('UNKNOWN'))
        else:
            # Handle unseen categories gracefully
            df['CompoundEncoded'] = df['Compound'].fillna('UNKNOWN').apply(
                lambda x: self.compound_encoder.transform([x])[0] if x in self.compound_encoder.classes_ else -1
            )
            df['DriverEncoded'] = df['Driver'].fillna('UNKNOWN').apply(
                lambda x: self.driver_encoder.transform([x])[0] if x in self.driver_encoder.classes_ else -1
            )
            df['TeamEncoded'] = df['Team'].fillna('UNKNOWN').apply(
                lambda x: self.team_encoder.transform([x])[0] if x in self.team_encoder.classes_ else -1
            )

        # Core features
        features = pd.DataFrame({
            'TyreLife': df['TyreLife'],
            'Compound': df['CompoundEncoded'],
            'LapNumber': df['LapNumber'],
            'Position': df['Position'].fillna(10),  # Default mid-field position
            'Stint': df['Stint'],
            'Driver': df['DriverEncoded'],
            'Team': df['TeamEncoded'],
        })

        # Add weather if available
        if 'AirTemp' in df.columns:
            features['AirTemp'] = df['AirTemp'].fillna(df['AirTemp'].median())
        if 'TrackTemp' in df.columns:
            features['TrackTemp'] = df['TrackTemp'].fillna(df['TrackTemp'].median())
        if 'Rainfall' in df.columns:
            features['Rainfall'] = df['Rainfall'].fillna(0)

        # Engineered features
        features['TyreLife_Squared'] = features['TyreLife'] ** 2
        features['LapProgress'] = df['LapNumber'] / df['LapNumber'].max()  # Fuel effect proxy

        self.feature_names = features.columns.tolist()

        return features.values

    def train(self, data: pd.DataFrame) -> Dict:
        """
        Train the tire degradation model

        Args:
            data: DataFrame with columns: LapTimeSeconds (target), TyreLife, Compound, etc.

        Returns:
            Training metrics dictionary
        """
        print(f"Training {self.model_type} model...")

        # Prepare features and target
        X = self.prepare_features(data, fit_encoders=True)
        y = data['LapTimeSeconds'].values

        # Remove any NaN values
        valid_idx = ~np.isnan(y)
        X = X[valid_idx]
        y = y[valid_idx]

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train model
        self.model.fit(X_train_scaled, y_train)
        self.is_fitted = True

        # Evaluate
        train_pred = self.model.predict(X_train_scaled)
        test_pred = self.model.predict(X_test_scaled)

        metrics = {
            'train_mae': mean_absolute_error(y_train, train_pred),
            'test_mae': mean_absolute_error(y_test, test_pred),
            'train_r2': r2_score(y_train, train_pred),
            'test_r2': r2_score(y_test, test_pred),
            'train_samples': len(X_train),
            'test_samples': len(X_test)
        }

        print(f"✅ Model trained!")
        print(f"  Train MAE: {metrics['train_mae']:.3f}s | R²: {metrics['train_r2']:.3f}")
        print(f"  Test MAE:  {metrics['test_mae']:.3f}s | R²: {metrics['test_r2']:.3f}")

        return metrics

    def predict_lap_time(self, tire_life: int, compound: str, lap_number: int,
                        position: int = 10, stint: int = 1, driver: str = 'UNKNOWN',
                        team: str = 'UNKNOWN', air_temp: float = 25.0,
                        track_temp: float = 35.0, rainfall: bool = False) -> float:
        """
        Predict lap time for given conditions

        Args:
            tire_life: Laps on current tire
            compound: Tire compound (SOFT, MEDIUM, HARD)
            lap_number: Current lap number
            position: Current position
            stint: Current stint number
            driver: Driver name
            team: Team name
            air_temp: Air temperature (°C)
            track_temp: Track temperature (°C)
            rainfall: Whether it's raining

        Returns:
            Predicted lap time (seconds)
        """
        if not self.is_fitted:
            raise ValueError("Model must be trained before prediction")

        # Create input dataframe
        input_data = pd.DataFrame([{
            'TyreLife': tire_life,
            'Compound': compound,
            'LapNumber': lap_number,
            'Position': position,
            'Stint': stint,
            'Driver': driver,
            'Team': team,
            'AirTemp': air_temp,
            'TrackTemp': track_temp,
            'Rainfall': 1 if rainfall else 0,
            'LapTimeSeconds': 0  # Dummy value
        }])

        # Prepare features
        X = self.prepare_features(input_data, fit_encoders=False)
        X_scaled = self.scaler.transform(X)

        # Predict
        prediction = self.model.predict(X_scaled)[0]

        return prediction

    def predict_stint_degradation(self, compound: str, max_laps: int = 30,
                                  **kwargs) -> pd.DataFrame:
        """
        Predict lap time degradation over a stint

        Args:
            compound: Tire compound
            max_laps: Maximum laps to predict
            **kwargs: Other parameters (lap_number, position, etc.)

        Returns:
            DataFrame with predictions for each lap
        """
        predictions = []

        for tire_life in range(1, max_laps + 1):
            lap_time = self.predict_lap_time(
                tire_life=tire_life,
                compound=compound,
                **kwargs
            )
            predictions.append({
                'TyreLife': tire_life,
                'Compound': compound,
                'PredictedLapTime': lap_time
            })

        return pd.DataFrame(predictions)

    def get_optimal_stint_length(self, compound: str, threshold_seconds: float = 2.0,
                                 **kwargs) -> int:
        """
        Find optimal stint length before tire degradation becomes critical

        Args:
            compound: Tire compound
            threshold_seconds: Lap time degradation threshold (vs fresh tire)
            **kwargs: Other parameters

        Returns:
            Optimal number of laps before pit stop
        """
        stint_pred = self.predict_stint_degradation(compound, max_laps=50, **kwargs)

        fresh_tire_time = stint_pred.iloc[0]['PredictedLapTime']
        critical_laps = stint_pred[
            stint_pred['PredictedLapTime'] > fresh_tire_time + threshold_seconds
        ]

        if len(critical_laps) == 0:
            return 50  # Can run full stint

        return int(critical_laps.iloc[0]['TyreLife'])

    def save_model(self, filepath: str = 'tire_model.pkl'):
        """Save trained model to disk"""
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted model")

        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'compound_encoder': self.compound_encoder,
            'driver_encoder': self.driver_encoder,
            'team_encoder': self.team_encoder,
            'feature_names': self.feature_names,
            'model_type': self.model_type
        }

        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)

        print(f"✅ Model saved to {filepath}")

    def load_model(self, filepath: str = 'tire_model.pkl'):
        """Load trained model from disk"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)

        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.compound_encoder = model_data['compound_encoder']
        self.driver_encoder = model_data['driver_encoder']
        self.team_encoder = model_data['team_encoder']
        self.feature_names = model_data['feature_names']
        self.model_type = model_data['model_type']
        self.is_fitted = True

        print(f"✅ Model loaded from {filepath}")


def plot_tire_degradation(model: TireDegradationModel, compounds: list = ['SOFT', 'MEDIUM', 'HARD'],
                          save_path: str = None):
    """
    Visualize tire degradation curves for different compounds

    Args:
        model: Trained TireDegradationModel
        compounds: List of compounds to compare
        save_path: Optional path to save plot
    """
    plt.figure(figsize=(10, 6))

    for compound in compounds:
        stint_pred = model.predict_stint_degradation(
            compound=compound,
            max_laps=40,
            lap_number=20,
            position=5
        )

        plt.plot(stint_pred['TyreLife'], stint_pred['PredictedLapTime'],
                label=compound, linewidth=2, marker='o', markersize=3)

    plt.xlabel('Tire Life (laps)', fontsize=12)
    plt.ylabel('Predicted Lap Time (seconds)', fontsize=12)
    plt.title('Tire Degradation Comparison', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Plot saved to {save_path}")

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    # Example usage
    from data_processor import F1DataProcessor

    print("=" * 60)
    print("TIRE DEGRADATION MODEL - Training Example")
    print("=" * 60)

    # Load data
    processor = F1DataProcessor(2024, 'Monaco')
    processor.load_race_data()
    lap_data = processor.extract_lap_features()

    print(f"\n📊 Training data: {len(lap_data)} laps")

    # Train model
    tire_model = TireDegradationModel(model_type='gradient_boost')
    metrics = tire_model.train(lap_data)

    # Test predictions
    print("\n🔮 PREDICTION EXAMPLES:")
    print("\nSoft tire degradation:")
    for lap in [1, 10, 20, 30]:
        pred = tire_model.predict_lap_time(
            tire_life=lap,
            compound='SOFT',
            lap_number=lap,
            position=5
        )
        print(f"  Lap {lap:2d}: {pred:.3f}s")

    print("\nOptimal stint lengths:")
    for compound in ['SOFT', 'MEDIUM', 'HARD']:
        optimal = tire_model.get_optimal_stint_length(
            compound=compound,
            threshold_seconds=1.5,
            lap_number=20
        )
        print(f"  {compound:6s}: {optimal} laps")

    # Save model
    tire_model.save_model('tire_model.pkl')

    # Visualize
    print("\n📈 Generating degradation plot...")
    plot_tire_degradation(tire_model, save_path='tire_degradation.png')

    print("\n✅ Tire model ready for pit stop optimizer!")
