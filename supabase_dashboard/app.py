import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
import datetime
import joblib
import numpy as np
import os
import time
# ---------------------------
# Supabase Configuration
# ---------------------------
SUPABASE_URL = "https://ymryienhepwknzqpaket.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InltcnlpZW5oZXB3a256cXBha2V0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI0OTMyNzksImV4cCI6MjA3ODA2OTI3OX0.AG-NfY2RcENjCX1BjH7hqGFwYFzMOWbF2A899zFh_AU"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------
# Load XGBoost Model
# ---------------------------
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "irrigation_xgb_model.pkl")
try:
    model = joblib.load(os.path.abspath(MODEL_PATH))
    st.success("✅ Smart Irrigation Model Loaded")
except Exception as e:
    st.error(f"❌ Failed to load XGBoost model: {e}")
    model = None
# ---------------------------
# Page Settings
# ---------------------------
st.set_page_config(
    page_title="Smart Irrigation Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("🌾 Smart Irrigation Dashboard")

# ---------------------------
# Fetch Sensor Data
# ---------------------------
@st.cache_data(ttl=10)
def fetch_sensor_data(limit=200):
    try:
        response = supabase.table("sensor_readings").select("*").order("timestamp", desc=True).limit(limit).execute()
        data = pd.DataFrame(response.data)
        if not data.empty:
            data["timestamp"] = pd.to_datetime(data["timestamp"])
            data.sort_values("timestamp", inplace=True)
        return data
    except Exception as e:
        st.warning(f"Failed to fetch data: {e}")
        return pd.DataFrame()

data = fetch_sensor_data(200)

# ---------------------------
# Predict Irrigation
# ---------------------------
def predict_irrigation(row):
    if model is None or row.empty:
        return 0

    features = ["soil_temp", "air_temp", "soil_moisture", "humidity", "light"]

    # Convert all relevant columns to numeric (in case they're strings)
    for col in features:
        row[col] = pd.to_numeric(row[col], errors="coerce")

    # Derived features
    row["temp_diff"] = row["air_temp"] - row["soil_temp"]
    row["humidity_ratio"] = row["humidity"] / (row["soil_moisture"] + 1)

    # Prepare input
    X = row[features + ["temp_diff", "humidity_ratio"]]

    # Handle any NaN values (in case of conversion failure)
    X = X.fillna(0)

    pred = model.predict(X)
    return int(pred[0])


# ---------------------------
# Dashboard Main
# ---------------------------
if data.empty:
    st.warning("No sensor data available.")
else:
    latest = data.iloc[-1]

    # Predict irrigation using model
    latest_irrigation = predict_irrigation(latest.to_frame().T)

    # ---------------------------
    # Metrics Display
    # ---------------------------
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Soil Moisture (%)", f"{latest.soil_moisture:.1f}")
    col2.metric("Air Temperature (°C)", f"{latest.air_temp:.1f}")
    col3.metric("Soil Temperature (°C)", f"{latest.soil_temp:.1f}")
    col4.metric("Humidity (%)", f"{latest.humidity:.1f}")

    # ---------------------------
    # Irrigation Status Alert
    # ---------------------------
    if latest_irrigation == 1:
        st.error(f"💧 IRRIGATION NEEDED! Soil Moisture={latest.soil_moisture:.1f}%")
    else:
        st.success(f"💧 No Irrigation Needed. Soil Moisture={latest.soil_moisture:.1f}%")

    # ---------------------------
    # Charts for Visualization
    # ---------------------------
    st.subheader("📊 Sensor Trends")

    # Soil Moisture & Humidity
    fig1 = px.line(
        data, x="timestamp", y=["soil_moisture", "humidity"],
        labels={"value": "Percentage", "timestamp": "Time"},
        title="Soil Moisture & Humidity Over Time"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Air & Soil Temperature
    fig2 = px.line(
        data, x="timestamp", y=["air_temp", "soil_temp"],
        labels={"value": "Temperature (°C)", "timestamp": "Time"},
        title="Air & Soil Temperature Over Time"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Light Intensity
    fig3 = px.line(
        data, x="timestamp", y="light",
        labels={"light": "Light Intensity", "timestamp": "Time"},
        title="Light Intensity Over Time"
    )
    st.plotly_chart(fig3, use_container_width=True)

# ---------------------------
# Sidebar Controls
# ---------------------------
st.sidebar.header("⚙️ Dashboard Controls")
refresh_sec = st.sidebar.slider("Auto-refresh interval (seconds)", min_value=5, max_value=60, value=15)
st.sidebar.markdown(f"Last refresh: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
# Auto-refresh
time.sleep(refresh_sec)
st.rerun()
st.sidebar.markdown(f"Last refresh: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ---------------------------
# Auto-refresh
# ---------------------------
st.session_state['rerun'] = True
st.query_params.update({"refresh": datetime.datetime.now().strftime("%H:%M:%S")})