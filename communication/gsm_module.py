import serial, time
from datetime import datetime
from utils.logger import get_logger

logger = get_logger("data/gsm.log")

# NOTE: change device path to your modem's serial device (check dmesg or /dev/ttyUSB*)
SERIAL_PORT = "/dev/ttyUSB3"   # TODO: change to correct port
BAUDRATE = 115200

def send_sms(phone_number, message, port=SERIAL_PORT):
    """
    Sends SMS using AT commands. Keep message short.
    """
    try:
        gsm = serial.Serial(port, baudrate=BAUDRATE, timeout=2)
        time.sleep(0.5)
        def write(cmd, wait=0.5):
            gsm.write(cmd if isinstance(cmd, bytes) else str(cmd).encode('utf-8'))
            time.sleep(wait)
        write('AT\r\n', 0.5)
        write('AT+CMGF=1\r\n', 0.5)   # text mode
        write(f'AT+CMGS="{phone_number}"\r\n', 0.5)
        # message terminated by Ctrl+Z
        write(message)
        write(bytes([26]), 0.5)
        time.sleep(2)
        logger.info("SMS sent to %s: %s", phone_number, message)
        gsm.close()
    except Exception as e:
        logger.exception("Failed to send SMS: %s", e)
        raise
def send_offline_alert(message):
    with open("data/outbox/alerts.txt", "a") as f:
        f.write(f"{datetime.now().isoformat()} - {message}\n")
