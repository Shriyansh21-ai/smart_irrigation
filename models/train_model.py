import os
import pandas as pd
from glob import glob
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier
import joblib
from datetime import datetime
import numpy as np

# 🔄 Auto-detect data folder
def find_data_folder():
    possible_paths = [
        os.path.join(os.getcwd(), "data"),           # ./data
        os.path.join(os.path.dirname(__file__), "../data"),  # ../data
        os.path.join(os.path.dirname(__file__), "data")      # models/data
    ]
    for path in possible_paths:
        if os.path.exists(path) and any(f.endswith(".csv") for f in os.listdir(path)):
            print(f"📁 Found data folder: {path}")
            return path
    raise FileNotFoundError("❌ No CSV files found in any 'data' folder. Please add data to ./data or ../data")

DATA_PATH = find_data_folder()
MODEL_PATH = "models/irrigation_xgb_model.pkl"
REPORT_PATH = "models/xgb_training_report.txt"


def load_all_data():
    csv_files = glob(os.path.join(DATA_PATH, "*.csv"))
    if not csv_files:
        raise FileNotFoundError("❌ No CSV files found in data directory.")

    dataframes = []
    for f in csv_files:
        try:
            df = pd.read_csv(f)
            df.columns = [col.strip().lower() for col in df.columns]
            if len(df) > 0:
                dataframes.append(df)
                print(f"📄 Loaded: {os.path.basename(f)} ({len(df)} rows)")
            else:
                print(f"⚠️ Skipped {f}: Empty file")
        except Exception as e:
            print(f"⚠️ Skipped {f}: {e}")

    merged = pd.concat(dataframes, ignore_index=True)
    print(f"✅ Total merged data shape: {merged.shape}")
    return merged


def preprocess_data(df):
    df.dropna(how="all", inplace=True)
    df = df.loc[:, ~df.columns.duplicated()]
    df.columns = [c.strip().lower() for c in df.columns]

    rename_map = {
        "light_intensity": "light",
        "luminosity": "light",
        "illumination": "light",
        "soiltemperature": "soil_temp",
        "airtemperature": "air_temp",
        "soilmoisture": "soil_moisture"
    }
    df.rename(columns=rename_map, inplace=True)

    if "light" not in df.columns:
        print("⚠️ 'light' column missing — generating mock light data (temporary).")
        df["light"] = np.random.uniform(200, 1000, size=len(df))

    required_cols = ["soil_temp", "air_temp", "soil_moisture", "humidity", "light"]
    for col in required_cols:
        if col not in df.columns:
            print(f"⚠️ Missing {col}, filling with mean or default 0.")
            df[col] = df[col].fillna(df[col].mean() if df[col].notna().any() else 0)

    df["temp_diff"] = df["air_temp"] - df["soil_temp"]
    df["humidity_ratio"] = df["humidity"] / (df["soil_moisture"] + 1)

    if "irrigation_needed" not in df.columns:
        print("⚠️ 'irrigation_needed' missing — auto-generating (soil_moisture < 30%).")
        df["irrigation_needed"] = (df["soil_moisture"] < 30).astype(int)
    else:
        df["irrigation_needed"] = df["irrigation_needed"].apply(
            lambda x: 1 if str(x).lower() in ["yes", "1", "true"] else 0
        )

    print(f"✅ Preprocessed data shape: {df.shape}")
    if len(df) < 10:
        print("⚠️ Too few samples (<10). Generating mock data for training demo.")
        df = generate_mock_data(df)
    return df


def generate_mock_data(df):
    np.random.seed(42)
    new_data = pd.DataFrame({
        "soil_temp": np.random.uniform(10, 35, 100),
        "air_temp": np.random.uniform(15, 40, 100),
        "soil_moisture": np.random.uniform(10, 90, 100),
        "humidity": np.random.uniform(30, 90, 100),
        "light": np.random.uniform(200, 1000, 100),
    })
    new_data["temp_diff"] = new_data["air_temp"] - new_data["soil_temp"]
    new_data["humidity_ratio"] = new_data["humidity"] / (new_data["soil_moisture"] + 1)
    new_data["irrigation_needed"] = (new_data["soil_moisture"] < 35).astype(int)
    return new_data


def train_xgboost_model(df):
    features = ["soil_temp", "air_temp", "soil_moisture", "humidity", "light", "temp_diff", "humidity_ratio"]
    target = "irrigation_needed"

    X = df[features]
    y = df[target]

    if len(X) < 2:
        raise ValueError("❌ Not enough data for training.")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("\n🚀 Training XGBoost model...")
    model = XGBClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=8,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='logloss',
        use_label_encoder=False,
        n_jobs=-1
    )

    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    print("\n📊 Model Evaluation Report:")
    print(classification_report(y_test, preds))
    print(f"✅ Accuracy: {acc * 100:.2f}%")

    # ensure models directory exists before saving the file
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"💾 Model saved: {MODEL_PATH}")

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("🌾 SMART IRRIGATION - XGBOOST TRAINING REPORT 🌾\n")
        f.write(f"Date: {datetime.now()}\n")
        f.write(f"Samples used: {len(df)}\n")
        f.write(f"Accuracy: {acc * 100:.2f}%\n\n")
        f.write("Feature Columns:\n")
        for col in features:
            f.write(f"- {col}\n")
    print("📝 Training report saved as models/xgb_training_report.txt")


if __name__ == "__main__":
    print("🌱 Starting Smart Irrigation XGBoost Training...\n")
    try:
        df = load_all_data()
        clean_df = preprocess_data(df)
        train_xgboost_model(clean_df)
        print("\n🎉 Training completed successfully with XGBoost!")
    except FileNotFoundError as e:
        print(f"❌ {e}")
    except Exception as e:
        print(f"❌ Unexpected error during training: {e}")
    finally:
        print("🔚 Exiting training script.")