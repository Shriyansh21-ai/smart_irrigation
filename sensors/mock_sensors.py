import random
from datetime import datetime

def get_mock_readings():
    """Simulate sensor readings for testing without hardware"""
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "soil_temp": round(random.uniform(18, 35), 2),       # °C
        "air_temp": round(random.uniform(20, 40), 2),        # °C
        "soil_moisture": round(random.uniform(20, 90), 2),   # %
        "humidity": round(random.uniform(40, 90), 2),        # %
        "light": round(random.uniform(200, 1000), 2)         # Lux
    }
