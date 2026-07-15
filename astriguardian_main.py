import requests
import streamlit as st

def fetch_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto"
    }

    r = requests.get(url, params=params)
    data = r.json()

    # DEBUG: Show raw API response if missing fields
    if "daily" not in data or "current_weather" not in data:
        st.error("Open‑Meteo returned incomplete weather data.")
        st.json(data)
        return None

    return data


def fetch_air(lat, lon):
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "pm10,pm2_5,european_aqi",
        "timezone": "auto"
    }

    r = requests.get(url, params=params)
    data = r.json()

    # DEBUG: Show raw API response if missing fields
    if "hourly" not in data:
        st.error("Open‑Meteo returned incomplete air quality data.")
        st.json(data)
        return None

    return data
