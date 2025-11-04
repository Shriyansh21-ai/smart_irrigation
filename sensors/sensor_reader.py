# unified sensor reader - uses mock_sensors by default
from sensors.mock_sensors import get_mock_readings


# If you have actual sensors, swap imports below and implement functions
# from ds18b20_template import get_soil_temperature
# from sht31d_template import get_air_data
# from sen0193_template import get_soil_moisture
# from bh1750_template import get_light_intensity

def read_all_sensors():
    """
    Returns a dict:
    {
      'soil_moisture': float (0-100),
      'soil_temp': float (deg C),
      'air_temp': float,
      'humidity': float (0-100),
      'light': float (lux)
    }
    """
    # For initial development use mock
    return get_mock_readings()
