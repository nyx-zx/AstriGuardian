import streamlit as st
import requests
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# ---------------------------------------------------------
# CONFIG & LIQUIDGLASS STYLE
# ---------------------------------------------------------
st.set_page_config(page_title="AstriGuardian – EarthGuardian", layout="wide")

st.markdown("""
<style>
.liquidglass {
    background: rgba(255,255,255,0.70);
    padding: 20px;
    border-radius: 22px;
    border: 1px solid rgba(200,200,200,0.6);
    backdrop-filter: blur(18px);
}
</style>
""", unsafe_allow_html=True)

st.title("🛰️ AstriGuardian – EarthGuardian Dashboard")

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
st.sidebar.header("Location")
lat = st.sidebar.number_input("Latitude", value=8.98, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=-79.52, format="%.4f")
days_ahead = st.sidebar.slider("Days to predict", 1, 7, 3)

st.sidebar.write("Data: Open-Meteo (hourly weather + air quality)")

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
        "hourly": "temperature_2m",
        "timezone": "auto",
    }
    r = requests.get(WEATHER_URL, params=params)
    data = r.json()
    if "hourly" not in data or "current_weather" not in data:
        st.error("Weather data incomplete.")
        st.json(data)
        return None
    return data

def fetch_air(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "pm10,pm2_5,european_aqi",
        "timezone": "auto",
    }
    r = requests.get(AIR_URL, params=params)
    data = r.json()
    if "hourly" not in data:
        st.error("Air quality data incomplete.")
        st.json(data)
        return None
    return data

# ---------------------------------------------------------
# FETCH DATA
# ---------------------------------------------------------
weather = fetch_weather(lat, lon)
air = fetch_air(lat, lon)

if weather is None or air is None:
    st.stop()

hourly_weather = weather["hourly"]
current = weather["current_weather"]
hourly_air = air["hourly"]

df_temp = pd.DataFrame({
    "time": hourly_weather["time"],
    "temp": hourly_weather["temperature_2m"],
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
# TOP WIDGETS: MAP + CURRENT WEATHER
# ---------------------------------------------------------
col_map, col_current = st.columns([1, 2])

with col_map:
    st.markdown('<div class="liquidglass">', unsafe_allow_html=True)
    st.subheader("📍 Location")
    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))
    st.markdown("</div>", unsafe_allow_html=True)

with col_current:
    st.markdown('<div class="liquidglass">', unsafe_allow_html=True)
    st.subheader("🌤 Current Weather")
    c1, c2, c3 = st.columns(3)
    c1.metric("Temperature (°C)", current["temperature"])
    c2.metric("Wind speed (m/s)", current["windspeed"])
    c3.metric("Wind direction (°)", current["winddirection"])
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# HOURLY TEMPERATURE WIDGET
# ---------------------------------------------------------
st.markdown('<div class="liquidglass">', unsafe_allow_html=True)
st.subheader("📈 Hourly temperature")
st.line_chart(df_temp[["temp"]])
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# AIR QUALITY WIDGET
# ---------------------------------------------------------
st.markdown('<div class="liquidglass">', unsafe_allow_html=True)
st.subheader("💨 Air quality (European AQI)")
st.line_chart(df_air[["aqi"]])
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# PREDICTIONS (ML + WIDGETS)
# ---------------------------------------------------------
st.markdown('<div class="liquidglass">', unsafe_allow_html=True)
st.subheader("🔮 Predictions")

# Build simple ML model on hourly temps
df_temp_sorted = df_temp.reset_index().copy()
df_temp_sorted["t_index"] = np.arange(len(df_temp_sorted))
X = df_temp_sorted[["t_index"]].values
y = df_temp_sorted["temp"].values

if len(X) > 10:
    model = LinearRegression()
    model.fit(X, y)

    # Predict next N days (assuming 24 hours per day)
    hours_per_day = 24
    last_index = df_temp_sorted["t_index"].iloc[-1]
    future_days = []
    for d in range(1, days_ahead + 1):
        start = last_index + (d - 1) * hours_per_day + 1
        end = last_index + d * hours_per_day
        future_indices = np.arange(start, end).reshape(-1, 1)
        preds = model.predict(future_indices)
        future_days.append({
            "day_offset": d,
            "min_pred": float(np.min(preds)),
            "max_pred": float(np.max(preds)),
        })

    # Horizontal widgets for predictions
    st.markdown("##### Upcoming days (prediction widgets)")
    cols = st.columns(len(future_days))
    for i, day in enumerate(future_days):
        with cols[i]:
            st.markdown("###### Day +" + str(day["day_offset"]))
            st.write(f"Min: {day['min_pred']:.1f}°C")
            st.write(f"Max: {day['max_pred']:.1f}°C")
else:
    st.write("Not enough data for ML predictions yet.")

# Current day summary widget
st.markdown("##### Today summary")
c1, c2 = st.columns(2)
with c1:
    st.write(f"Current temperature: **{current['temperature']}°C**")
with c2:
    current_aqi = hourly_air["european_aqi"][0]
    st.write(f"Current AQI: **{current_aqi}** (lower is better)")

st.caption("AstriGuardian – ML predictions based on hourly temperature using scikit-learn.")
st.markdown("</div>", unsafe_allow_html=True)
