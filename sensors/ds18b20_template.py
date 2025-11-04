# ds18b20_template.py
# Example using w1thermsensor; enable 1-wire on Pi and attach probe.
from w1thermsensor import W1ThermSensor

sensor = W1ThermSensor()

def get_soil_temperature():
    try:
        return sensor.get_temperature()
    except Exception as e:
        raise
