from supabase import create_client, Client

# --- Your Supabase credentials ---
SUPABASE_URL = "https://ymryienhepwknzqpaket.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InltcnlpZW5oZXB3a256cXBha2V0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI0OTMyNzksImV4cCI6MjA3ODA2OTI3OX0.AG-NfY2RcENjCX1BjH7hqGFwYFzMOWbF2A899zFh_AU"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def log_sensor_data(data: dict):
    """Insert one reading into Supabase."""
    try:
        response = supabase.table("sensor_readings").insert(data).execute()
        print("✅ Data logged to Supabase:", response.data)
    except Exception as e:
        print("❌ Supabase logging error:", e)
