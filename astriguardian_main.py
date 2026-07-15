import streamlit as st
import requests
import pandas as pd

# -------------------------------
# STREAMLIT CONFIG & STYLES
# -------------------------------
st.set_page_config(page_title="AstriGuardian – EarthGuardian", layout="wide")

st.markdown("""
<style>
.glass {
    background: rgba(255,255,255,0.70);
    padding: 20px;
    border-radius: 18px;
    border: 1px solid rgba(200,200,200,0.6);
    backdrop-filter: blur(12px);
}
</style>
""", unsafe_allow_html=True)

st.title("🛰️ AstriGuardian – EarthGuardian Dashboard")

# -------------------------------
# SIDEBAR CONTROLS
# -------------------------------
st.sidebar.header("Location")
lat = st.sidebar.number_input("Latitude", value=8.98, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=-79.52, format="%.4f")
days = st.sidebar.slider("Forecast days", 1, 7, 5)

st.sidebar.write("Data source: Open-Meteo (weather + air quality)")

# -------------------------------
# FETCH FUNCTIONS
# -------------------------------
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


def fetch_weather(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
    }
    r = requests.get(WEATHER_URL, params=params)
    data = r.json()

    if "daily" not in data or "current_weather" not in data:
        st.error("Open-Meteo did not return complete weather data.")
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
        st.error("Open-Meteo did not return air quality data.")
        st.json(data)
        return None
    return data


# -------------------------------
# FETCH DATA
# -------------------------------
weather = fetch_weather(lat, lon)
air = fetch_air(lat, lon)

if weather is None or air is None:
    st.stop()

daily = weather["daily"]
current = weather["current_weather"]
hourly_air = air["hourly"]

# -------------------------------
# TOP: MAP + CURRENT WEATHER
# -------------------------------
col_map, col_current = st.columns([1, 2])

with col_map:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("📍 Location")
    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))
    st.markdown("</div>", unsafe_allow_html=True)

with col_current:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("🌤 Current Weather")
    c1, c2, c3 = st.columns(3)
    c1.metric("Temperature (°C)", current["temperature"])
    c2.metric("Wind speed (m/s)", current["windspeed"])
    c3.metric("Wind direction (°)", current["winddirection"])
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# DAILY TEMPERATURE FORECAST
# -------------------------------
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.subheader("📈 Daily temperature forecast")

df_daily = pd.DataFrame({
    "date": daily["time"][:days],
    "temp_max": daily["temperature_2m_max"][:days],
    "temp_min": daily["temperature_2m_min"][:days],
}).set_index("date")

st.line_chart(df_daily)
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# AIR QUALITY GRAPH
# -------------------------------
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.subheader("💨 Air quality (European AQI)")

df_air = pd.DataFrame({
    "time": hourly_air["time"],
    "aqi": hourly_air["european_aqi"],
    "pm10": hourly_air["pm10"],
    "pm2_5": hourly_air["pm2_5"],
}).set_index("time")

st.line_chart(df_air[["aqi"]])
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# SIMPLE PREDICTION
# -------------------------------
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.subheader("🔮 AstriGuardian prediction")

today_max = daily["temperature_2m_max"][0]
today_min = daily["temperature_2m_min"][0]
current_aqi = hourly_air["european_aqi"][0]

st.write(f"🌡 Today: between **{today_min}°C** and **{today_max}°C**.")
st.write(f"💨 Current AQI: **{current_aqi}** (lower is better).")

st.caption("Prototype AstriGuardian – extend with ML models, alerts, and more.")
st.markdown("</div>", unsafe_allow_html=True)
