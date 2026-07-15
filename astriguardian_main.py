# astriguardian.py
import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="AstriGuardian", layout="wide")

# Liquid glass CSS
st.markdown("""
<style>
.glass {
    background: rgba(255,255,255,0.65);
    padding: 20px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.35);
    backdrop-filter: blur(12px);
}
</style>
""", unsafe_allow_html=True)

st.title("🛰️ AstriGuardian – EarthGuardian Dashboard")

# Sidebar
st.sidebar.header("Location")
lat = st.sidebar.number_input("Latitude", value=8.98)
lon = st.sidebar.number_input("Longitude", value=-79.52)
days = st.sidebar.slider("Forecast days", 1, 7, 5)

# Open-Meteo endpoints
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

# Weather request
weather_params = {
    "latitude": lat,
    "longitude": lon,
    "current_weather": True,
    "daily": "temperature_2m_max,temperature_2m_min",
    "timezone": "auto"
}
weather = requests.get(WEATHER_URL, params=weather_params).json()

# Air quality request
air_params = {
    "latitude": lat,
    "longitude": lon,
    "hourly": "pm10,pm2_5,european_aqi",
    "timezone": "auto"
}
air = requests.get(AIR_URL, params=air_params).json()

# MAP + CURRENT WEATHER
col1, col2 = st.columns([1,2])

with col1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("📍 Location")
    st.map(pd.DataFrame({"lat":[lat], "lon":[lon]}))
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("🌤 Current Weather")
    cw = weather.get("current_weather")
    if cw:
        c1, c2, c3 = st.columns(3)
        c1.metric("Temperature", f"{cw['temperature']} °C")
        c2.metric("Wind Speed", f"{cw['windspeed']} m/s")
        c3.metric("Wind Direction", f"{cw['winddirection']}°")
    else:
        st.warning("No current weather data available.")
    st.markdown('</div>', unsafe_allow_html=True)

# DAILY FORECAST GRAPH
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.subheader("📈 Temperature Forecast")

daily = weather.get("daily")
if daily:
    df_daily = pd.DataFrame({
        "date": daily["time"][:days],
        "temp_max": daily["temperature_2m_max"][:days],
        "temp_min": daily["temperature_2m_min"][:days],
    }).set_index("date")
    st.line_chart(df_daily)
else:
    st.warning("No daily forecast available.")
st.markdown('</div>', unsafe_allow_html=True)

# AIR QUALITY GRAPH
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.subheader("💨 Air Quality (European AQI)")

hourly_air = air.get("hourly")
if hourly_air:
    df_air = pd.DataFrame({
        "time": hourly_air["time"],
        "aqi": hourly_air["european_aqi"],
        "pm10": hourly_air["pm10"],
        "pm2_5": hourly_air["pm2_5"],
    }).set_index("time")
    st.line_chart(df_air[["aqi"]])
else:
    st.warning("No air quality data available.")
st.markdown('</div>', unsafe_allow_html=True)

# PREDICTION
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.subheader("🔮 AstriGuardian Prediction")

if daily:
    today_max = daily["temperature_2m_max"][0]
    today_min = daily["temperature_2m_min"][0]
    st.write(f"🌡 Today: **{today_min}°C – {today_max}°C**")

if hourly_air:
    current_aqi = hourly_air["european_aqi"][0]
    st.write(f"💨 AQI: **{current_aqi}** (lower is better)")

st.markdown('</div>', unsafe_allow_html=True)
