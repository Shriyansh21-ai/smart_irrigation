import csv
from datetime import datetime

def log_data(sensor_data, decision, reason, water_saved):
    with open("data/logs.csv", "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            sensor_data.get('soil_temp'),
            sensor_data.get('air_temp'),
            sensor_data.get('soil_moisture'),
            sensor_data.get('humidity'),
            sensor_data.get('light'),
            decision,
            reason,
            water_saved
        ])

def calculate_water_saved(prev_moisture, curr_moisture):
    delta = max(0, prev_moisture - curr_moisture)
    return round(delta * 0.1, 2)  # Example conversion
