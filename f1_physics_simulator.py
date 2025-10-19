"""
F1 Physics-Based Racing Simulator - REALISTIC VERSION
Calibrated to match real F1 performance: 0-100 km/h in 2.6s

Key: Traction-limited at low speed (no AWD, no TC, minimal downforce)
"""

import numpy as np
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Tuple, Optional
import math


@dataclass
class CarState:
    """Current state of the F1 car"""
    # Position
    x: float = 0.0
    y: float = 0.0
    heading: float = 0.0  # radians

    # Velocity
    speed: float = 0.0  # m/s
    vx: float = 0.0
    vy: float = 0.0

    # Controls
    throttle: float = 0.0  # 0-100
    brake: float = 0.0     # 0-100
    steering: float = 0.0  # -1 to 1

    # State
    gear: int = 1
    rpm: int = 0
    tire_temp: float = 80.0  # Celsius
    fuel_kg: float = 100.0

    # Lap info
    lap_time: float = 0.0
    distance: float = 0.0


@dataclass
class CarPhysics:
    """F1 2024 Car Physics Parameters - REAL SPECIFICATIONS"""

    # Mass (FIA regulations 2024)
    mass: float = 798.0  # kg (minimum weight including driver, excluding fuel)

    # Aerodynamics (realistic F1 values)
    drag_coefficient: float = 0.9  # Higher for realistic acceleration
    frontal_area: float = 1.5  # m²
    downforce_coefficient: float = 3.0  # Generates ~2x weight at 190 km/h

    # Engine (1.6L V6 Turbo Hybrid - Real F1 2024)
    max_power: float = 710000.0  # Watts (950 HP with hybrid system)
    max_rpm: int = 15000  # FIA limit
    idle_rpm: int = 5000  # Higher idle for F1
    power_curve_peak: int = 11000  # Peak power RPM for turbocharged engine

    # Gearbox
    gear_ratios: List[float] = None
    final_drive: float = 3.5

    # Brakes (Carbon-Carbon F1 brakes)
    max_brake_force: float = 18000.0  # Newtons (realistic for 798kg car)
    brake_balance: float = 0.58  # 58% front (typical F1)

    # Tires (Pirelli F1 - REAL LIMITED GRIP at low speed)
    tire_grip_coefficient: float = 1.4  # Peak grip with downforce
    tire_optimal_temp: float = 90.0  # Celsius
    tire_optimal_slip: float = 10.0  # Degrees

    # Track
    track_friction: float = 1.0  # Dry asphalt

    def __post_init__(self):
        if self.gear_ratios is None:
            # F1 8-speed gearbox ratios
            self.gear_ratios = [3.5, 2.8, 2.2, 1.8, 1.5, 1.3, 1.15, 1.0]


class F1PhysicsSimulator:
    """Simulates F1 car physics using real equations - CALIBRATED VERSION"""

    def __init__(self, physics: CarPhysics = None):
        self.physics = physics or CarPhysics()
        self.dt = 0.01  # 100 Hz simulation (10ms timesteps)

        # Constants
        self.air_density = 1.2  # kg/m³
        self.gravity = 9.81  # m/s²

    def calculate_engine_power(self, rpm: int, throttle: float) -> float:
        """
        Calculate engine power based on RPM and throttle
        F1 engines have a torque curve that peaks around 11000 RPM
        """
        if rpm < self.physics.idle_rpm:
            rpm = self.physics.idle_rpm
        if rpm > self.physics.max_rpm:
            rpm = self.physics.max_rpm

        # Power curve (simplified Gaussian around peak RPM)
        rpm_ratio = rpm / self.physics.power_curve_peak
        power_factor = math.exp(-0.5 * ((rpm_ratio - 1.0) ** 2) / 0.3)

        # Apply throttle
        power = self.physics.max_power * power_factor * (throttle / 100.0)

        return power

    def calculate_aerodynamic_forces(self, speed: float) -> Tuple[float, float]:
        """
        Calculate drag and downforce

        Returns:
            (drag_force, downforce)
        """
        # Drag: F = 0.5 * ρ * v² * Cd * A
        drag = 0.5 * self.air_density * (speed ** 2) * \
               self.physics.drag_coefficient * self.physics.frontal_area

        # Downforce: F = 0.5 * ρ * v² * Cl * A
        downforce = 0.5 * self.air_density * (speed ** 2) * \
                    self.physics.downforce_coefficient * self.physics.frontal_area

        return drag, downforce

    def calculate_braking_force(self, brake_input: float, speed: float,
                                downforce: float) -> float:
        """
        Calculate braking force with ABS simulation
        """
        # Normal force (weight + downforce)
        normal_force = (self.physics.mass * self.gravity) + downforce

        # Max brake force limited by tire grip
        max_brake = normal_force * self.physics.tire_grip_coefficient

        # Apply brake input
        brake_force = min(
            self.physics.max_brake_force * (brake_input / 100.0),
            max_brake
        )

        return brake_force

    def update_car_state(self, state: CarState, throttle: float,
                        brake: float, steering: float) -> CarState:
        """
        Update car state based on REALISTIC F1 physics

        CRITICAL: Models traction limitation at low speed
        F1 cars have NO AWD, NO traction control - they wheelspin heavily 0-100 km/h!
        """
        # Update inputs
        state.throttle = np.clip(throttle, 0, 100)
        state.brake = np.clip(brake, 0, 100)
        state.steering = np.clip(steering, -1, 1)

        # Calculate aerodynamic forces (speed-dependent!)
        drag, downforce = self.calculate_aerodynamic_forces(state.speed)

        # Total normal force (weight + downforce)
        normal_force = (self.physics.mass * self.gravity) + downforce

        # Engine force calculation
        if state.gear >= 1 and state.gear <= len(self.physics.gear_ratios):
            gear_ratio = self.physics.gear_ratios[state.gear - 1]

            # Calculate RPM from speed and gear ratio
            if state.speed > 0.1:
                wheel_rpm = (state.speed * 60) / (2 * math.pi * 0.33)  # 0.33m wheel radius
                state.rpm = int(wheel_rpm * gear_ratio * self.physics.final_drive)
            else:
                state.rpm = self.physics.idle_rpm

            # Clamp RPM
            state.rpm = max(self.physics.idle_rpm, min(state.rpm, self.physics.max_rpm))

            # Get engine power
            power = self.calculate_engine_power(state.rpm, state.throttle)

            # === CRITICAL TRACTION MODELING ===
            # Key insight: F1 cars are traction-limited at low speed!
            # No AWD, no traction control, minimal downforce → massive wheelspin

            speed_kmh = state.speed * 3.6

            if speed_kmh < 100:  # Below 100 km/h - traction limited zone
                # Engine wants to deliver this much force
                if state.speed > 0.5:
                    desired_force = power / state.speed
                else:
                    # At near-zero speed, based on torque
                    desired_force = 10000.0 * (state.throttle / 100.0)

                # But traction is LIMITED without downforce!
                # Base tire grip without much aero help
                base_grip = 0.85  # Much lower than peak

                # Grip improves gradually as speed builds (downforce effect)
                speed_factor = speed_kmh / 100.0  # 0.0 at 0 km/h, 1.0 at 100 km/h
                effective_grip = base_grip + (self.physics.tire_grip_coefficient - base_grip) * speed_factor

                # Maximum traction force
                max_traction = normal_force * effective_grip

                # Engine force LIMITED by traction
                engine_force = min(desired_force, max_traction)

            else:
                # Above 100 km/h: good downforce, less wheelspin
                engine_force = power / state.speed

                # Still limit by available grip (but much higher now)
                max_traction = normal_force * self.physics.tire_grip_coefficient
                engine_force = min(engine_force, max_traction)
        else:
            engine_force = 0
            state.rpm = self.physics.idle_rpm

        # Braking force
        brake_force = self.calculate_braking_force(state.brake, state.speed, downforce)

        # Net longitudinal force
        net_force = engine_force - drag - brake_force

        # Acceleration: F = ma  =>  a = F/m
        acceleration = net_force / self.physics.mass

        # Update speed
        state.speed = max(0, state.speed + acceleration * self.dt)

        # Turning (simplified bicycle model)
        if abs(state.steering) > 0.01:
            steering_angle = state.steering * math.radians(30)
            wheelbase = 3.6  # F1 wheelbase ~3.6m
            turning_radius = wheelbase / math.tan(abs(steering_angle))
            angular_velocity = state.speed / turning_radius * np.sign(state.steering)
            state.heading += angular_velocity * self.dt
            state.heading = state.heading % (2 * math.pi)

        # Update position
        state.vx = state.speed * math.cos(state.heading)
        state.vy = state.speed * math.sin(state.heading)
        state.x += state.vx * self.dt
        state.y += state.vy * self.dt

        # Update distance and time
        state.distance += state.speed * self.dt
        state.lap_time += self.dt

        # Auto gearbox (shift at 95% max RPM)
        if state.rpm > self.physics.max_rpm * 0.95 and state.gear < 8:
            state.gear += 1
        elif state.rpm < self.physics.max_rpm * 0.5 and state.gear > 1:
            state.gear -= 1

        return state


def main():
    """Test realistic F1 physics"""
    print("\n" + "="*80)
    print("F1 PHYSICS SIMULATOR - REALISTIC VERSION")
    print("="*80 + "\n")

    print("Target: 0-100 km/h in 2.6s (real F1)")
    print("Target: 0-200 km/h in 4.5s (real F1)\n")

    sim = F1PhysicsSimulator()
    state = CarState()

    time = 0.0
    time_to_100 = None
    time_to_200 = None

    while time < 10.0:
        state = sim.update_car_state(state, throttle=100, brake=0, steering=0)
        time += sim.dt

        speed_kmh = state.speed * 3.6

        if speed_kmh >= 100 and time_to_100 is None:
            time_to_100 = time
            print(f"✓ Reached 100 km/h in {time:.2f}s")

        if speed_kmh >= 200 and time_to_200 is None:
            time_to_200 = time
            print(f"✓ Reached 200 km/h in {time:.2f}s")
            break

    print(f"\nResults:")
    print(f"  0-100 km/h: {time_to_100:.2f}s (Target: 2.6s)")
    print(f"  0-200 km/h: {time_to_200:.2f}s (Target: 4.5s)")

    if abs(time_to_100 - 2.6) < 0.3 and abs(time_to_200 - 4.5) < 0.5:
        print("\n🏆 PHYSICS VALIDATED - MATCHES REAL F1!")
    else:
        print("\n⚠️  Physics needs further calibration")


if __name__ == '__main__':
    main()
