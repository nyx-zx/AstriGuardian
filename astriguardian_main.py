# astriguardian_app.py
import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="AstriGuardian - EarthGuardian", layout="wide")

st.title("🛰️ AstriGuardian – EarthGuardian Dashboard")

st.sidebar.header("Location settings")
lat = st.sidebar.number_input("Latitude", value=8.98, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=-79.52, format="%.4f")
days = st.sidebar.slider("Days to forecast", 1, 7, 5)

st.sidebar.write("Data source: Open-Meteo")

# --- Open-Meteo endpoints ---
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

# --- Fetch weather ---
params_weather = {
    "latitude": lat,
    "longitude": lon,
    "daily": ["temperature_2m_max", "temperature_2m_min"],
    "current_weather": True,
    "timezone": "auto"
}
weather_resp = requests.get(WEATHER_URL, params=params_weather)
weather = weather_resp.json()

# --- Fetch air quality ---
params_air = {
    "latitude": lat,
    "longitude": lon,
    "hourly": ["pm10", "pm2_5", "european_aqi"],
    "timezone": "auto"
}
air_resp = requests.get(AIR_URL, params=params_air)
air = air_resp.json()

# --- Layout ---
col_map, col_info = st.columns([1, 2])

with col_map:
    st.subheader("Location")
    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))

with col_info:
    st.subheader("Current conditions")
    if "current_weather" in weather:
        cw = weather["current_weather"]
        st.metric("Temperature (°C)", cw["temperature"])
        st.metric("Wind speed (m/s)", cw["windspeed"])
    else:
        st.warning("No current weather data available.")

# --- Daily forecast graph ---
st.subheader("Daily temperature forecast")

daily = weather.get("daily", {})
if daily:
    df_daily = pd.DataFrame({
        "date": daily["time"][:days],
        "temp_max": daily["temperature_2m_max"][:days],
        "temp_min": daily["temperature_2m_min"][:days],
    })
    df_daily.set_index("date", inplace=True)
    st.line_chart(df_daily)
else:
    st.warning("No daily forecast data available.")

# --- Air quality graph ---
st.subheader("Air quality (European AQI)")

hourly_air = air.get("hourly", {})
if hourly_air:
    df_air = pd.DataFrame({
        "time": hourly_air["time"],
        "aqi": hourly_air["european_aqi"],
        "pm10": hourly_air["pm10"],
        "pm2_5": hourly_air["pm2_5"],
    })
    df_air.set_index("time", inplace=True)
    st.line_chart(df_air[["aqi"]])
else:
    st.warning("No air quality data available.")

# --- Simple prediction text ---
st.subheader("AstriGuardian prediction")

if daily:
    today_max = daily["temperature_2m_max"][0]
    today_min = daily["temperature_2m_min"][0]
    st.write(f"🌍 Today: between **{today_min}°C** and **{today_max}°C**.")
    if hourly_air:
        current_aqi = hourly_air["european_aqi"][0]
        st.write(f"💨 Current AQI: **{current_aqi}** (lower is better).")
else:
    st.write("No forecast data to generate prediction.")

st.caption("Prototype AstriGuardian – extend with ML models, alerts, and more.")

