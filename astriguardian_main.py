# astriguardian.py
import streamlit as st
import pandas as pd
from openmeteo_sdk import OpenMeteo

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

# Open-Meteo client
om = OpenMeteo()

# WEATHER FORECAST
weather = om.forecast(
    latitude=lat,
    longitude=lon,
    current_weather=True,
    daily=["temperature_2m_max", "temperature_2m_min"],
    timezone="auto"
)

# AIR QUALITY
air = om.air_quality(
    latitude=lat,
    longitude=lon,
    hourly=["pm10", "pm2_5", "european_aqi"],
    timezone="auto"
)

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
    cw = weather["current_weather"]
    st.metric("Temperature", f"{cw['temperature']} °C")
    st.metric("Wind Speed", f"{cw['windspeed']} m/s")
    st.metric("Wind Direction", f"{cw['winddirection']}°")
    st.markdown('</div>', unsafe_allow_html=True)

# DAILY FORECAST GRAPH
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.subheader("📈 Temperature Forecast")

df_daily = pd.DataFrame({
    "date": weather["daily"]["time"][:days],
    "temp_max": weather["daily"]["temperature_2m_max"][:days],
    "temp_min": weather["daily"]["temperature_2m_min"][:days],
}).set_index("date")

st.line_chart(df_daily)
st.markdown('</div>', unsafe_allow_html=True)

# AIR QUALITY GRAPH
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.subheader("💨 Air Quality (European AQI)")

df_air = pd.DataFrame({
    "time": air["hourly"]["time"],
    "aqi": air["hourly"]["european_aqi"],
    "pm10": air["hourly"]["pm10"],
    "pm2_5": air["hourly"]["pm2_5"],
}).set_index("time")

st.line_chart(df_air[["aqi"]])
st.markdown('</div>', unsafe_allow_html=True)

# PREDICTION
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.subheader("🔮 AstriGuardian Prediction")

today_max = weather["daily"]["temperature_2m_max"][0]
today_min = weather["daily"]["temperature_2m_min"][0]
current_aqi = air["hourly"]["european_aqi"][0]

st.write(f"🌡 Today: **{today_min}°C – {today_max}°C**")
st.write(f"💨 AQI: **{current_aqi}** (lower is better)")
st.markdown('</div>', unsafe_allow_html=True)
