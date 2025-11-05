import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))



from flask import Flask, render_template, jsonify, request
import os, csv, threading, time
from datetime import datetime
from sensors.mock_sensors import get_mock_readings
from models.decision_engine import decide_irrigation

app = Flask(__name__)

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/live_log.csv")
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/sensor_data")
def sensor_data():
    data = get_mock_readings()
    decision = decide_irrigation(data)
    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["irrigation"] = "ON" if decision == 1 else "OFF"
    
    # Log data
    with open(DATA_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if f.tell() == 0:
            writer.writeheader()
        writer.writerow(data)
    
    return jsonify(data)

@app.route("/api/chatbot", methods=["POST"])
def chatbot():
    query = request.json.get("query", "").lower()
    data = get_mock_readings()
    response = "Sorry, I didn’t understand that."

    if "moisture" in query:
        response = f"Soil moisture is {data['soil_moisture']:.1f}%."
    elif "temperature" in query:
        response = f"Air {data['air_temp']:.1f}°C, Soil {data['soil_temp']:.1f}°C."
    elif "humidity" in query:
        response = f"Humidity is {data['humidity']:.1f}%."
    elif "light" in query:
        response = f"Light intensity is {data['light']:.1f} lux."
    elif "irrigation" in query:
        decision = decide_irrigation(data)
        response = "Irrigation is ON." if decision == 1 else "Irrigation is OFF."
    elif "status" in query:
        response = f"Soil: {data['soil_moisture']:.1f}% | Air: {data['air_temp']:.1f}°C | Light: {data['light']:.1f} lux"

    return jsonify({"response": response})

if __name__ == "__main__":
    print("✅ Smart Irrigation Dashboard running...")
    app.run(debug=True)
