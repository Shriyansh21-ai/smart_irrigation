import csv
import random
import time
from datetime import datetime

def generate_mock_data(num_samples=1000, delay=0.0):
    """
    Generate mock sensor data for smart irrigation project.
    Saves data to 'sensor_data.csv'
    """

    # Define realistic environmental ranges
    soil_temp_range = (15, 38)       # °C
    air_temp_range = (18, 42)        # °C
    soil_moisture_range = (10, 90)   # %
    humidity_range = (30, 95)        # %
    light_range = (100, 1200)        # Lux

    # Open CSV file
    with open("sensor_data.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp",
            "soil_temp",
            "air_temp",
            "soil_moisture",
            "humidity",
            "light_intensity",
            "irrigation_status"
        ])

        for _ in range(num_samples):
            soil_temp = round(random.uniform(*soil_temp_range), 2)
            air_temp = round(random.uniform(*air_temp_range), 2)
            soil_moisture = round(random.uniform(*soil_moisture_range), 2)
            humidity = round(random.uniform(*humidity_range), 2)
            light = round(random.uniform(*light_range), 2)

            # Generate irrigation status label
            # 0 = Normal, 1 = Under-irrigated, 2 = Over-irrigated
            if soil_moisture < 30:
                irrigation_status = 1  # Under-irrigated
            elif soil_moisture > 70:
                irrigation_status = 2  # Over-irrigated
            else:
                irrigation_status = 0  # Normal

            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                soil_temp,
                air_temp,
                soil_moisture,
                humidity,
                light,
                irrigation_status
            ])

            if delay > 0:
                time.sleep(delay)

    print(f"✅ Mock dataset generated: sensor_data.csv ({num_samples} samples)")

if __name__ == "__main__":
    # Generate 1000 samples instantly
    generate_mock_data(num_samples=1000, delay=0)
