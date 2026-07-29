import streamlit as st
import requests
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# ---------------------------------------------------------
# STREAMLIT CONFIG & LIQUIDGLASS STYLE
# ---------------------------------------------------------
st.set_page_config(page_title="AstriGuardian – EarthGuardian", layout="wide")

st.markdown("""
<style>
.liquidglass {
    background: rgba(255,255,255,0.55);
    padding: 22px;
    border-radius: 25px;
    border: 1px solid rgba(255,255,255,0.35);
    backdrop-filter: blur(18px);
    box-shadow: 0 4px 25px rgba(0,0,0,0.15);
    transition: all 0.3s ease;
}
.liquidglass:hover {
    transform: scale(1.02);
}
.predcard {
    background: rgba(255,255,255,0.45);
    padding: 18px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.25);
    backdrop-filter: blur(14px);
    margin-right: 15px;
    min-width: 180px;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)

st.title("🛰️ AstriGuardian — EarthGuardian Dashboard")

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
st.sidebar.header("Location")
lat = st.sidebar.number_input("Latitude", value=8.98, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=-79.52, format="%.4f")
days_ahead = st.sidebar.slider("Days to predict", 1, 7, 3)

st.sidebar.write("Data: Open-Meteo (hourly weather + air quality)")

# ---------------------------------------------------------
# API ENDPOINTS
# ---------------------------------------------------------
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

# ---------------------------------------------------------
# FETCH FUNCTIONS
# ---------------------------------------------------------
def fetch_weather(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": "temperature_2m,relativehumidity_2m,dewpoint_2m",
        "timezone": "auto",
    }
    r = requests.get(WEATHER_URL, params=params)
    return r.json()

def fetch_air(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "pm10,pm2_5,european_aqi",
        "timezone": "auto",
    }
    r = requests.get(AIR_URL, params=params)
    return r.json()

# ---------------------------------------------------------
# FETCH DATA
# ---------------------------------------------------------
weather = fetch_weather(lat, lon)
air = fetch_air(lat, lon)

if "hourly" not in weather or "current_weather" not in weather:
    st.error("Weather data incomplete.")
    st.json(weather)
    st.stop()

if "hourly" not in air:
    st.error("Air quality data incomplete.")
    st.json(air)
    st.stop()

hourly_weather = weather["hourly"]
current = weather["current_weather"]
hourly_air = air["hourly"]

# ---------------------------------------------------------
# DATAFRAMES
# ---------------------------------------------------------
df_temp = pd.DataFrame({
    "time": hourly_weather["time"],
    "temp": hourly_weather["temperature_2m"],
    "humidity": hourly_weather["relativehumidity_2m"],
    "dew": hourly_weather["dewpoint_2m"],
})
df_temp["date"] = df_temp["time"].str.slice(0, 10)
df_temp.set_index("time", inplace=True)

df_air = pd.DataFrame({
    "time": hourly_air["time"],
    "aqi": hourly_air["european_aqi"],
    "pm10": hourly_air["pm10"],
    "pm2_5": hourly_air["pm2_5"],
})
df_air.set_index("time", inplace=True)

# ---------------------------------------------------------
# WIDGETS: MAP + CURRENT WEATHER
# ---------------------------------------------------------
col_map, col_current = st.columns([1, 2])

with col_map:
    st.markdown('<div class="liquidglass">', unsafe_allow_html=True)
    st.subheader("📍 Location")
    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))
    st.markdown("</div>", unsafe_allow_html=True)

with col_current:
    st.markdown('<div class="liquidglass">', unsafe_allow_html=True)
    st.subheader("🌤 Current Weather (LiquidGlass Widget)")
    st.write(f"### {current['temperature']}°C")
    st.write(f"**Wind:** {current['windspeed']} m/s")
    st.write(f"**Direction:** {current['winddirection']}°")
    st.write(f"**Humidity:** {df_temp['humidity'].iloc[-1]}%")
    st.write(f"**Dew Point:** {df_temp['dew'].iloc[-1]}°C")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# HOURLY TEMPERATURE WIDGET
# ---------------------------------------------------------
st.markdown('<div class="liquidglass">', unsafe_allow_html=True)
st.subheader("📈 Hourly Temperature (LiquidGlass Widget)")
st.line_chart(df_temp[["temp"]])
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# AIR QUALITY WIDGET
# ---------------------------------------------------------
st.markdown('<div class="liquidglass">', unsafe_allow_html=True)
st.subheader("💨 Air Quality (LiquidGlass Widget)")
st.line_chart(df_air[["aqi"]])
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# ML PREDICTIONS
# ---------------------------------------------------------
st.markdown('<div class="liquidglass">', unsafe_allow_html=True)
st.subheader("🔮 Predictions (LiquidGlass Widgets + ML)")

# Build ML model
df_temp_sorted = df_temp.reset_index().copy()
df_temp_sorted["t_index"] = np.arange(len(df_temp_sorted))
X = df_temp_sorted[["t_index"]].values
y = df_temp_sorted["temp"].values

future_days = []

if len(X) > 10:
    model = LinearRegression()
    model.fit(X, y)

    hours_per_day = 24
    last_index = df_temp_sorted["t_index"].iloc[-1]

    for d in range(1, days_ahead + 1):
        start = last_index + (d - 1) * hours_per_day + 1
        end = last_index + d * hours_per_day
        future_indices = np.arange(start, end).reshape(-1, 1)
        preds = model.predict(future_indices)
        future_days.append({
            "day": d,
            "min": float(np.min(preds)),
            "max": float(np.max(preds)),
        })

# ---------------------------------------------------------
# HORIZONTAL SCROLL WIDGETS
# ---------------------------------------------------------
st.write("### Scrollable Prediction Widgets")

scroll = st.container()
with scroll:
    st.markdown('<div style="white-space: nowrap; overflow-x: auto;">', unsafe_allow_html=True)

    for day in future_days:
        st.markdown(
            f"""
            <div class="predcard">
                <h4>Day +{day['day']}</h4>
                <p>Min: {day['min']:.1f}°C</p>
                <p>Max: {day['max']:.1f}°C</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)

st.caption("AstriGuardian — ML predictions using scikit-learn.")
st.markdown("</div>", unsafe_allow_html=True)
