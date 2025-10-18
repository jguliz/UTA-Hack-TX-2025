import fastf1
import pandas as pd
import numpy as np
import os

# Setup cache
cache_dir = 'fastf1_cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
fastf1.Cache.enable_cache(cache_dir)

print("=" * 60)
print("FASTF1 DATA QUALITY VALIDATION")
print("=" * 60)

# Load session
session = fastf1.get_session(2024, 'Monaco', 'R')
session.load()

print(f"\n✅ Session: {session.event['EventName']} - {session.event['EventDate']}")

# 1. VALIDATE RACE RESULTS
print("\n" + "=" * 60)
print("1. RACE RESULTS VALIDATION")
print("=" * 60)
results = session.results
print(f"Total drivers with results: {len(results)}")
print(f"Columns available: {list(results.columns)}")

# Check for complete finishing positions
complete_results = results[results['Position'].notna()]
print(f"✅ Drivers with valid positions: {len(complete_results)}")

# Verify winner
winner = results[results['Position'] == 1.0].iloc[0]
print(f"✅ Winner: {winner['Abbreviation']} ({winner['FullName']}) - {winner['TeamName']}")

# 2. VALIDATE LAP DATA
print("\n" + "=" * 60)
print("2. LAP DATA VALIDATION")
print("=" * 60)
all_laps = session.laps
print(f"Total laps recorded: {len(all_laps)}")
print(f"Lap data columns: {list(all_laps.columns)}")

# Check for missing critical data
critical_lap_fields = ['LapTime', 'LapNumber', 'Driver', 'Compound', 'TyreLife']
for field in critical_lap_fields:
    missing = all_laps[field].isna().sum()
    total = len(all_laps)
    pct_complete = ((total - missing) / total) * 100
    status = "✅" if pct_complete > 95 else "⚠️"
    print(f"{status} {field}: {pct_complete:.1f}% complete ({total - missing}/{total})")

# 3. VALIDATE TELEMETRY DATA
print("\n" + "=" * 60)
print("3. TELEMETRY DATA VALIDATION")
print("=" * 60)

# Test telemetry for multiple drivers
test_drivers = ['LEC', 'VER', 'NOR', 'PIA', 'SAI']
telemetry_success = []

for driver in test_drivers:
    try:
        driver_laps = session.laps.pick_drivers(driver)  # Using new method
        if len(driver_laps) > 0:
            fastest = driver_laps.pick_fastest()
            telem = fastest.get_telemetry()
            
            # Check critical telemetry fields
            required_fields = ['Speed', 'X', 'Y', 'Throttle', 'Brake', 'nGear', 'RPM']
            all_present = all(field in telem.columns for field in required_fields)
            
            if all_present:
                telemetry_success.append(driver)
                print(f"✅ {driver}: {len(telem)} data points, {len(driver_laps)} laps")
            else:
                print(f"⚠️ {driver}: Missing some telemetry fields")
    except Exception as e:
        print(f"❌ {driver}: Error - {str(e)}")

print(f"\nTelemetry working for {len(telemetry_success)}/{len(test_drivers)} test drivers")

# 4. VALIDATE PIT STOP DATA
print("\n" + "=" * 60)
print("4. PIT STOP DATA VALIDATION")
print("=" * 60)

pit_stops = all_laps[all_laps['PitOutTime'].notna()]
print(f"Total pit stops detected: {len(pit_stops)}")

# Group by driver
pit_summary = pit_stops.groupby('Driver').agg({
    'LapNumber': list,
    'Compound': list
}).reset_index()

print(f"✅ Drivers who pitted: {len(pit_summary)}")
print("\nPit stop breakdown (sample):")
for idx, row in pit_summary.head(5).iterrows():
    print(f"   {row['Driver']}: Laps {row['LapNumber']} → {row['Compound']}")

# 5. VALIDATE POSITION/GPS DATA
print("\n" + "=" * 60)
print("5. POSITION (GPS) DATA VALIDATION")
print("=" * 60)

# Check if we have X,Y coordinates for track mapping
fastest_lap = session.laps.pick_fastest()
track_data = fastest_lap.get_telemetry()

has_position = all(col in track_data.columns for col in ['X', 'Y', 'Z'])
print(f"✅ GPS coordinates available: {has_position}")

if has_position:
    x_range = track_data['X'].max() - track_data['X'].min()
    y_range = track_data['Y'].max() - track_data['Y'].min()
    print(f"✅ Track dimensions: {x_range:.0f}m x {y_range:.0f}m")
    print(f"✅ Position data points: {len(track_data)}")
    
    # Check for any null positions
    null_positions = track_data[['X', 'Y']].isna().sum().sum()
    print(f"✅ Null position values: {null_positions} (should be 0 or very low)")

# 6. VALIDATE TIRE COMPOUND DATA
print("\n" + "=" * 60)
print("6. TIRE COMPOUND DATA VALIDATION")
print("=" * 60)

compounds_used = all_laps['Compound'].value_counts()
print("Tire compound usage:")
for compound, count in compounds_used.items():
    print(f"   {compound}: {count} laps")

# Check if compound data is complete
compound_missing = all_laps['Compound'].isna().sum()
compound_pct = ((len(all_laps) - compound_missing) / len(all_laps)) * 100
print(f"✅ Compound data completeness: {compound_pct:.1f}%")

# 7. VALIDATE WEATHER DATA
print("\n" + "=" * 60)
print("7. WEATHER DATA VALIDATION")
print("=" * 60)

weather = session.weather_data
print(f"Weather data points: {len(weather)}")
print(f"Weather columns: {list(weather.columns)}")

if len(weather) > 0:
    print(f"✅ Temperature range: {weather['AirTemp'].min():.1f}°C - {weather['AirTemp'].max():.1f}°C")
    print(f"✅ Track temp range: {weather['TrackTemp'].min():.1f}°C - {weather['TrackTemp'].max():.1f}°C")
    print(f"✅ Humidity: {weather['Humidity'].mean():.1f}%")
    rainfall = weather['Rainfall'].sum() > 0
    print(f"✅ Rain during race: {'Yes' if rainfall else 'No'}")

# 8. FINAL SUMMARY
print("\n" + "=" * 60)
print("SUMMARY - DATA QUALITY FOR AI MODELING")
print("=" * 60)

checks = {
    "Race results": len(complete_results) >= 15,
    "Lap times": all_laps['LapTime'].notna().sum() > 1000,
    "Telemetry": len(telemetry_success) >= 3,
    "Pit stops": len(pit_stops) > 15,
    "GPS tracking": has_position,
    "Tire data": compound_pct > 95,
    "Weather data": len(weather) > 0
}

passed = sum(checks.values())
total = len(checks)

print(f"\n✅ Passed: {passed}/{total} critical checks")
for check, result in checks.items():
    status = "✅" if result else "❌"
    print(f"   {status} {check}")

if passed == total:
    print("\n🎉 ALL DATA VALIDATED - READY FOR AI DEVELOPMENT!")
    print("\nYou can reliably use this data for:")
    print("   • Pit stop strategy optimization")
    print("   • Tire degradation modeling")
    print("   • Race position prediction")
    print("   • Lap time forecasting")
    print("   • Track visualization and replay")
elif passed >= total * 0.8:
    print("\n⚠️ MOSTLY GOOD - Minor data gaps but workable")
else:
    print("\n❌ SIGNIFICANT DATA ISSUES - May need different race/session")

print("\n" + "=" * 60)