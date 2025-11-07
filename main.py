import os
import time
import pandas as pd
import logging
from datetime import datetime, timezone
from xgboost import XGBClassifier
import joblib
import random
from supabase import create_client, Client

# =============== CONFIG ===============
MODEL_PATH = "models/irrigation_xgb_model.pkl"

SUPABASE_URL = "https://ymryienhepwknzqpaket.supabase.co"  
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InltcnlpZW5oZXB3a256cXBha2V0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI0OTMyNzksImV4cCI6MjA3ODA2OTI3OX0.AG-NfY2RcENjCX1BjH7hqGFwYFzMOWbF2A899zFh_AU"  

OFFLINE_BACKUP = "offline_backup.csv"
UPLOAD_INTERVAL = 10  # seconds

# =============== LOGGING ===============
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# =============== INIT SUPABASE ===============
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logging.info("✅ Supabase client initialized successfully")
except Exception as e:
    supabase = None
    logging.warning(f"⚠️ Could not initialize Supabase: {e}")

# =============== LOAD MODEL ===============
try:
    model = joblib.load(MODEL_PATH)
    logging.info("✅ XGBoost model loaded successfully")
except Exception as e:
    model = None
    logging.error(f"❌ Failed to load model: {e}")

# =============== MOCK SENSOR DATA ===============
def read_sensor_data():
    """Simulate live sensor data readings."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "soil_temp": round(random.uniform(15, 35), 2),
        "air_temp": round(random.uniform(20, 40), 2),
        "soil_moisture": round(random.uniform(10, 90), 2),
        "humidity": round(random.uniform(30, 90), 2),
        "light": round(random.uniform(200, 1000), 2)
    }

# =============== UPLOAD / BACKUP HANDLING ===============
def upload_to_supabase(data):
    """Upload to Supabase or store locally if offline."""
    try:
        if not supabase:
            raise ConnectionError("Supabase client not initialized")

        response = supabase.table("sensor_readings").insert(data).execute()
        if response.data:
            logging.info("📤 Data uploaded to Supabase successfully.")
            return True
        else:
            raise Exception("Supabase returned no data")
    except Exception as e:
        logging.warning(f"⚠️ Upload failed ({e}). Saving offline...")
        pd.DataFrame([data]).to_csv(OFFLINE_BACKUP, mode="a", header=not os.path.exists(OFFLINE_BACKUP), index=False)
        return False


# =============== DECISION ENGINE ===============
def decide_irrigation(sensor_data):
    """Use trained ML model to decide irrigation need."""
    if not model:
        return "MODEL_NOT_AVAILABLE"

    features = [
        sensor_data["soil_temp"],
        sensor_data["air_temp"],
        sensor_data["soil_moisture"],
        sensor_data["humidity"],
        sensor_data["light"],
        sensor_data["air_temp"] - sensor_data["soil_temp"],
        sensor_data["humidity"] / (sensor_data["soil_moisture"] + 1)
    ]

    prediction = model.predict([features])[0]
    return "IRRIGATION" if prediction == 1 else "NO_IRRIGATION"


# =============== MAIN LOOP ===============
def main_loop():
    logging.info("🌱 Starting Smart Irrigation System (Supabase Integrated)...")

    while True:
        sensor_data = read_sensor_data()
        decision = decide_irrigation(sensor_data)

        msg = f"💧 {decision.replace('_', ' ')} | Soil Moisture={sensor_data['soil_moisture']}"
        logging.info(f"[{sensor_data['timestamp']}] {msg}")

        record = {
            **sensor_data,
            "decision": decision,
        }

        upload_to_supabase(record)
        time.sleep(UPLOAD_INTERVAL)


# =============== ENTRY POINT ===============
if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        logging.info("🛑 Stopped by user.")
