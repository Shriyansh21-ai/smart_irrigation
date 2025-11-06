import os
import time
import joblib
import logging
import pandas as pd
from datetime import datetime, timezone
from xgboost import XGBClassifier

# ---------------- Paths ----------------
MODEL_JSON_PATH = "models/irrigation_model.json"
MODEL_PKL_PATH = "models/irrigation_xgb_model.pkl"
DATA_LOG_PATH = "data/realtime_sensor_log.csv"

# ---------------- Logging Setup ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# ---------------- Sensor Mock Function ----------------
def read_sensors():
    """Mock sensor readings (replace with real sensor code later)."""
    import random
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "soil_temp": round(random.uniform(15, 35), 2),
        "air_temp": round(random.uniform(20, 40), 2),
        "soil_moisture": round(random.uniform(10, 90), 2),
        "humidity": round(random.uniform(30, 90), 2),
        "light": round(random.uniform(200, 1000), 2),
    }

# ---------------- Model Loader ----------------
def load_model():
    if os.path.exists(MODEL_PKL_PATH):
        logging.info(f"✅ Loading XGBoost model (PKL): {MODEL_PKL_PATH}")
        model = joblib.load(MODEL_PKL_PATH)
        return model
    elif os.path.exists(MODEL_JSON_PATH):
        logging.info(f"✅ Loading XGBoost model (JSON): {MODEL_JSON_PATH}")
        model = XGBClassifier()
        model.load_model(MODEL_JSON_PATH)
        return model
    else:
        raise FileNotFoundError("❌ No model found in models/ directory.")

# ---------------- Feature Preparation ----------------
def prepare_features(reading):
    df = pd.DataFrame([reading])
    df["temp_diff"] = df["air_temp"] - df["soil_temp"]
    df["humidity_ratio"] = df["humidity"] / (df["soil_moisture"] + 1)

    # Reorder columns exactly as in training
    cols = ["soil_temp", "air_temp", "soil_moisture", "humidity", "light", "temp_diff", "humidity_ratio"]
    return df[cols]

# ---------------- Prediction ----------------
def predict_irrigation(model, reading):
    df = prepare_features(reading)
    pred = model.predict(df)
    return int(pred[0])

# ---------------- Append Sensor Data ----------------
def append_reading(row_dict, label=''):
    os.makedirs(os.path.dirname(DATA_LOG_PATH), exist_ok=True)
    df = pd.DataFrame([{
        "timestamp": row_dict.get('timestamp', datetime.now(timezone.utc).isoformat()),
        "soil_temp": row_dict["soil_temp"],
        "air_temp": row_dict["air_temp"],
        "soil_moisture": row_dict["soil_moisture"],
        "humidity": row_dict["humidity"],
        "light": row_dict["light"],
        "irrigation_needed": label
    }])
    header = not os.path.exists(DATA_LOG_PATH)
    df.to_csv(DATA_LOG_PATH, mode='a', header=header, index=False)

# ---------------- Main Loop ----------------
def main_loop():
    try:
        model = load_model()
    except Exception as e:
        logging.error(f"Failed to load model: {e}")
        return

    logging.info("Starting main loop")
    while True:
        try:
            reading = read_sensors()
            logging.info(f"Read sensors: {reading}")

            irrigation_needed = predict_irrigation(model, reading)
            if irrigation_needed == 1:
                logging.info(f"[{datetime.now().isoformat()}] 💧 Irrigation Needed! Soil moisture={reading['soil_moisture']}")
            else:
                logging.info(f"[{datetime.now().isoformat()}] INFO: No irrigation needed. Soil moisture={reading['soil_moisture']}")

            # Optional user feedback for supervised logging
            user_input = input("Confirm irrigation needed? (y=needed / n=not / Enter=skip): ").strip().lower()
            if user_input in ["y", "n"]:
                label = 1 if user_input == "y" else 0
                append_reading(reading, label)

            time.sleep(5)  # adjust interval as needed

        except KeyboardInterrupt:
            logging.info("🛑 Stopped by user.")
            break
        except Exception as e:
            logging.error(f"Unexpected error in main loop: {e}")

# ---------------- Entry Point ----------------
if __name__ == "__main__":
    main_loop()
