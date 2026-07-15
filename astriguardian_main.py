# astriguardian_app.py
import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="AstriGuardian – EarthGuardian", layout="wide")

# ---------- UI HEADER ----------
st.markdown(
    """
    <style>
    .glass-card {
        background: rgba(255, 255, 255, 0.75);
        border-radius: 18px;
        padding: 18px;
        border: 1px solid rgba(200, 200, 200, 0.6);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("## 🛰️ AstriGuardian – EarthGuardian Dashboard")

# ---------- SIDEBAR ----------
st.sidebar.markdown("### 🌍 Location")
lat = st.sidebar.number_input("Latitude", value=8.98, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=-79.52, format="%.4f")
days = st.sidebar.slider("Days to forecast", 1, 7, 5)

st.sidebar.markdown("Data source: **Open-Meteo**")

# ---------- OPEN-METEO CALLS ----------
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

# Weather params (note: daily params as comma-separated string)
weather_params = {
    "latitude": lat,
    "longitude": lon,
    "daily": "temperature_2m_max,temperature_2m_min",
    "current_weather": True,
    "timezone": "auto",
}
air_params = {
    "latitude": lat,
    "longitude": lon,
    "hourly": "pm10,pm2_5,european_aqi",
    "timezone": "auto",
}

weather_resp = requests.get(WEATHER_URL, params=weather_params)
air_resp = requests.get(AIR_URL, params=air_params)

weather = weather_resp.json()
air = air_resp.json()

# ---------- TOP LAYOUT ----------
col_map, col_current = st.columns([1, 2])

with col_map:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 📍 Location")
    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))
    st.markdown("</div>", unsafe_allow_html=True)

with col_current:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 🌤 Current conditions")
    cw = weather.get("current_weather")
    if cw:
        c1, c2, c3 = st.columns(3)
        c1.metric("Temperature (°C)", cw["temperature"])
        c2.metric("Wind speed (m/s)", cw["windspeed"])
        c3.metric("Direction (°)", cw["winddirection"])
    else:
        st.warning("No current weather data available from Open-Meteo.")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- DAILY FORECAST ----------
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("#### 📈 Daily temperature forecast")

daily = weather.get("daily")
if daily and "time" in daily:
    df_daily = pd.DataFrame({
        "date": daily["time"][:days],
        "temp_max": daily["temperature_2m_max"][:days],
        "temp_min": daily["temperature_2m_min"][:days],
    })
    df_daily.set_index("date", inplace=True)
    st.line_chart(df_daily)
else:
    st.warning("No daily forecast data available from Open-Meteo.")
st.markdown("</div>", unsafe_allow_html=True)

# ---------- AIR QUALITY ----------
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("#### 💨 Air quality (European AQI)")

hourly_air = air.get("hourly")
if hourly_air and "time" in hourly_air:
    df_air = pd.DataFrame({
        "time": hourly_air["time"],
        "aqi": hourly_air["european_aqi"],
        "pm10": hourly_air["pm10"],
        "pm2_5": hourly_air["pm2_5"],
    })
    df_air.set_index("time", inplace=True)
    st.line_chart(df_air[["aqi"]])
else:
    st.warning("No air quality data available from Open-Meteo.")
st.markdown("</div>", unsafe_allow_html=True)

# ---------- PREDICTION ----------
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("#### 🔮 AstriGuardian prediction")

if daily and "temperature_2m_max" in daily:
    today_max = daily["temperature_2m_max"][0]
    today_min = daily["temperature_2m_min"][0]
    st.write(f"Today looks between **{today_min}°C** and **{today_max}°C**.")

    if hourly_air and "european_aqi" in hourly_air:
        current_aqi = hourly_air["european_aqi"][0]
        st.write(f"Current AQI: **{current_aqi}** (lower is better).")
else:
    st.write("Not enough data to generate a prediction yet.")
st.markdown("</div>", unsafe_allow_html=True)

st.caption("Prototype AstriGuardian – extend with ML, alerts, and more liquid-glass UI.")

