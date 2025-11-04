#!/usr/bin/env python3
"""
Main control loop:
- reads sensors
- predicts irrigation_needed with model
- rule-based fallback
- triggers SMS alert (and can trigger relay via GPIO if implemented)
- collects user feedback (adaptive learning) and appends to CSV
"""

import time, os, csv, traceback
# avoid pandas dependency; build feature vectors as plain lists for model.predict
import importlib
try:
    xgb = importlib.import_module("xgboost")
    XGBOOST_AVAILABLE = True
except Exception:
    xgb = None
    XGBOOST_AVAILABLE = False
from datetime import datetime

# local imports
from sensors.sensor_reader import read_all_sensors
from communication.gsm_module import send_sms
from utils.logger import get_logger

# Optional conversational assistant
try:
    from utils.chat_assistant import ChatAssistant
    chat = ChatAssistant()  # may download model on first run
    CHAT_AVAILABLE = True
except Exception:
    CHAT_AVAILABLE = False

# Config
MODEL_PATH = "models/irrigation_model.json"
COLLECTED_CSV = "data/collected_data.csv"     # appended with feedback label
TRAINING_CSV = "data/training_data.csv"       # historical training data (can be same file)
LOG_FILE = "data/system.log"

# runtime settings
# PHONE_NUMBER can be provided via environment variable (e.g. +12345556789); if empty SMS will be skipped
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "")
# sleep interval between loop iterations (seconds)
SLEEP_SECONDS = int(os.getenv("SLEEP_SECONDS", "60"))

# ensure data directory exists
data_dir = os.path.dirname(COLLECTED_CSV) or "."
os.makedirs(data_dir, exist_ok=True)

# Load model
logger = get_logger(LOG_FILE)
model = None
if os.path.exists(MODEL_PATH) and XGBOOST_AVAILABLE and xgb is not None:
    try:
        model = xgb.XGBClassifier()
        model.load_model(MODEL_PATH)
        logger.info("Loaded model from %s", MODEL_PATH)
    except Exception as e:
        logger.exception("Failed to load model: %s", e)
        model = None
else:
    if not os.path.exists(MODEL_PATH):
        logger.warning("Model not found at %s. Will use rule-based fallback.", MODEL_PATH)
    else:
        logger.warning("xgboost is not available; skipping model load and using rule-based fallback.")

# Helper: append reading + optional label to CSV
def append_reading(row_dict, label=None, csv_path=COLLECTED_CSV):
    header = ['timestamp','soil_moisture','soil_temp','air_temp','humidity','light','label']
    exists = os.path.exists(csv_path)
    with open(csv_path, 'a', newline='') as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(header)
        row = [
            row_dict.get('timestamp', datetime.utcnow().isoformat()),
            row_dict['soil_moisture'],
            row_dict['soil_temp'],
            row_dict['air_temp'],
            row_dict['humidity'],
            row_dict['light'],
            label if label is not None else ''
        ]
        writer.writerow(row)

# Simple rule-based fallback
def rule_based_decision(data):
    # VERY simple: change thresholds for your crop; these are example baseline values
    soil_moisture = data['soil_moisture']
    humidity = data['humidity']
    # example rule: if soil moisture below 30 OR (moisture<40 and humidity<40)
    if soil_moisture < 30 or (soil_moisture < 40 and humidity < 40):
        return 1
    return 0

def predict_decision(data):
    # Build feature vector as a plain list to avoid pandas dependency
    X = [[
        data['soil_moisture'],
        data['soil_temp'],
        data['air_temp'],
        data['humidity'],
        data['light']
    ]]
    try:
        if model is not None:
            pred = model.predict(X)[0]
            logger.info("Model prediction: %s", pred)
            return int(pred)
    except Exception as e:
        logger.exception("Model inference failed, falling back to rule. Error: %s", e)
    return rule_based_decision(data)

def main_loop():
    logger.info("Starting main loop")
    while True:
        try:
            raw = read_all_sensors()
            logger.info("Read sensors: %s", raw)

            decision = predict_decision(raw)
            if decision == 1:
                msg = f"[{raw['timestamp']}] ALERT: Irrigation recommended. Soil moisture={raw['soil_moisture']}"
                logger.warning(msg)
                # Send SMS (non-blocking approach recommended in production)
                try:
                    if PHONE_NUMBER:
                        send_sms(PHONE_NUMBER, msg)
                    else:
                        logger.warning("PHONE_NUMBER not configured; skipping SMS alert. Message: %s", msg)
                except Exception as e:
                    logger.exception("Failed to send SMS: %s", e)
            else:
                msg = f"[{raw['timestamp']}] INFO: No irrigation needed. Soil moisture={raw['soil_moisture']}"
                logger.info(msg)

            # Save reading (without label yet)
            append_reading(raw, label='')

            # Ask for feedback (console) - this is simple; you can replace with mobile-confirmation later
            # Automatic feedback: if you actuate pump, you can use flow sensor reading to auto-label
            try:
                # Non-blocking minimal prompt: user can press Enter to skip
                feedback = input("Confirm irrigation needed? (y=needed / n=not / Enter=skip): ").strip().lower()
                label = None
                if feedback == 'y':
                    label = 1
                elif feedback == 'n':
                    label = 0

                if label is not None:
                    append_reading(raw, label=label)   # append with label
                    logger.info("User feedback saved: %s", label)
            except Exception as e:
                logger.debug("Feedback prompt skipped or failed: %s", e)

            # Optional: Chat assistant usage example
            if CHAT_AVAILABLE:
                q = f"Why irrigation? Soil moist={raw['soil_moisture']}, temp={raw['soil_temp']}, humid={raw['humidity']}."
                reply = chat.ask(q)
                print("Assistant:", reply)

        except KeyboardInterrupt:
            logger.info("Shutting down by user")
            break
        except Exception as e:
            logger.exception("Unexpected error in main loop: %s", e)

        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    main_loop()
