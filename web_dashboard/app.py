from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os

app = Flask(__name__)

DATA_CSV = "../data/collected_data.csv"

@app.route("/")
def index():
    if os.path.exists(DATA_CSV):
        df = pd.read_csv(DATA_CSV).dropna(axis=1, how='all')
        # show last 48 readings
        df_recent = df.tail(48)
        fig = px.line(df_recent, x="timestamp", y="soil_moisture", title="Soil Moisture (recent)")
        graph_html = pio.to_html(fig, full_html=False)
    else:
        graph_html = "<p>No data yet. Start main.py to collect readings.</p>"

    return render_template("index.html", graph_html=graph_html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
