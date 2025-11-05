import os
import joblib
import numpy as np

# Try loading trained model if available
MODEL_PATH = os.path.join(os.path.dirname(__file__), "irrigation_model.pkl")

model = None
if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
        print("✅ Loaded trained irrigation model.")
    except Exception as e:
        print(f"⚠️ Could not load model: {e}")
else:
    print("⚠️ Model file not found; using rule-based fallback.")

def decide_irrigation(data):
    """
    Decide if irrigation is needed.
    Input: dict with keys ['soil_temp', 'air_temp', 'soil_moisture', 'humidity', 'light']
    Output: 1 = irrigation needed, 0 = not needed
    """
    if model:
        try:
            features = np.array([
                data["soil_temp"],
                data["air_temp"],
                data["soil_moisture"],
                data["humidity"],
                data["light"]
            ]).reshape(1, -1)
            prediction = model.predict(features)[0]
            return int(prediction)
        except Exception as e:
            print(f"⚠️ Model prediction failed, using fallback. ({e})")

    # --- Fallback Rule-Based Logic ---
    if data["soil_moisture"] < 40:
        return 1  # Irrigation needed
    elif data["soil_moisture"] > 70:
        return 0  # Too wet, no irrigation
    elif data["air_temp"] > 35 and data["humidity"] < 50:
        return 1  # Hot and dry conditions
    else:
        return 0  # Default: not needed
