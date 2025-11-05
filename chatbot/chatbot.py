import os, sys, random
from datetime import datetime

# Add parent path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sensors.mock_sensors import get_mock_readings
from models.decision_engine import decide_irrigation

# Optional voice modules
try:
    import pyttsx3
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

# --- Voice helpers ---
def init_voice():
    if not VOICE_AVAILABLE:
        return None, None, False
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 170)
        recognizer = sr.Recognizer()
        with sr.Microphone() as _:
            pass  # confirm mic presence
        return engine, recognizer, True
    except Exception:
        return None, None, False

def speak(engine, text):
    print(f"🤖: {text}")
    if engine:
        engine.say(text)
        engine.runAndWait()

def listen(recognizer):
    """Return lower-case query string or empty on error."""
    with sr.Microphone() as source:
        print("🎙️ Listening... (say 'exit' to quit)")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)
        try:
            query = recognizer.recognize_google(audio).lower()
            print(f"🗣️ You said: {query}")
            return query
        except Exception:
            return ""

# --- Core logic ---
def handle_query(query, speak_fn):
    data = get_mock_readings()

    if "exit" in query or "quit" in query:
        speak_fn("Goodbye! Stay hydrated 🌱")
        return False
    elif "moisture" in query:
        speak_fn(f"Soil moisture is {data['soil_moisture']:.1f} percent.")
    elif "temperature" in query:
        speak_fn(f"Air temperature {data['air_temp']:.1f}°C, soil {data['soil_temp']:.1f}°C.")
    elif "humidity" in query:
        speak_fn(f"Humidity is {data['humidity']:.1f} percent.")
    elif "light" in query:
        speak_fn(f"Light intensity {data['light']:.1f} lux.")
    elif "status" in query or "sensor" in query:
        speak_fn(f"Air {data['air_temp']:.1f}°C, Soil {data['soil_temp']:.1f}°C, "
                 f"Moisture {data['soil_moisture']:.1f}%, Humidity {data['humidity']:.1f}%, "
                 f"Light {data['light']:.1f} lux.")
    elif "irrigation" in query:
        decision = decide_irrigation(data)
        if decision == 1:
            speak_fn(f"Soil moisture {data['soil_moisture']:.1f}%. Irrigation needed.")
        else:
            speak_fn(f"Soil moisture {data['soil_moisture']:.1f}%. No irrigation required.")
    elif "time" in query:
        speak_fn(f"The time is {datetime.now().strftime('%I:%M %p')}.")
    elif "help" in query:
        speak_fn("You can ask about moisture, temperature, humidity, light, irrigation, or say exit.")
    else:
        speak_fn("Sorry, I didn't understand. Try saying help.")
    return True

# --- Chatbot main ---
def chatbot():
    engine, recognizer, mic_ok = init_voice()
    use_voice = mic_ok
    speak(engine, "Smart irrigation assistant ready.")

    while True:
        if use_voice:
            query = listen(recognizer)
            if not query:
                speak(engine, "Could not hear you. Switching to text mode.")
                use_voice = False
                continue
        else:
            query = input("You: ").lower().strip()

        if not query:
            continue
        if not handle_query(query, lambda text: speak(engine, text)):
            break

if __name__ == "__main__":
    chatbot()
