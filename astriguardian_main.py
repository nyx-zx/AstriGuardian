import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="EarthGuardian Forecast",
    layout="wide"
)

# ---------------------------------------------------------
# WHITE LIQUID GLASS UI
# ---------------------------------------------------------
st.markdown("""
<style>

body {
    background: #f5f7fb !important;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top left, #ffffff 0%, #f0f4ff 40%, #e6ecff 100%);
}

.glass {
    border-radius: 24px;
    background: linear-gradient(to top right, rgba(255,255,255,0.85), rgba(255,255,255,0.65));
    backdrop-filter: blur(22px);
    box-shadow:
        0 18px 40px rgba(15, 23, 42, 0.18),
        inset 0 0 0 1px rgba(255,255,255,0.7);
    padding: 20px;
    transition: 0.25s;
}

.glass:hover {
    transform: translateY(-4px);
    box-shadow:
        0 24px 60px rgba(15, 23, 42, 0.25),
        inset 0 0 0 1px rgba(255,255,255,0.9);
}

.title {
    font-size: 28px;
    font-weight: 700;
    color: #111827;
}

.subtitle {
    font-size: 14px;
    color: #6b7280;
}

.value {
    font-size: 36px;
    font-weight: 700;
    color: #111827;
}

.forecast-card {
    border-radius: 20px;
    background: linear-gradient(to top right, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
    backdrop-filter: blur(18px);
    box-shadow:
        0 14px 32px rgba(15, 23, 42, 0.16),
        inset 0 0 0 1px rgba(255,255,255,0.8);
    padding: 14px 16px;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CITY LIST
# ---------------------------------------------------------
CITIES = {
    "Panamá, Panamá": (9.0, -79.5),
    "Colón": (9.35, -79.9),
    "David": (8.43, -82.43),
    "Santiago": (8.1, -80.97),
    "Chitré": (7.96, -80.43)
}

# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------
st.markdown("<h1 class='title' style='text-align:center;'>EarthGuardian — Liquid Glass Forecast</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle' style='text-align:center;'>Modern weather dashboard with forecast and map</p>", unsafe_allow_html=True)

# ---------------------------------------------------------
# SELECT CITY
# ---------------------------------------------------------
city = st.selectbox("Choose a city", list(CITIES.keys()))
lat, lon = CITIES[city]

# ---------------------------------------------------------
# OPEN-METEO BULK FORECAST (NO RATE LIMITS)
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_bulk(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "daily": [
            "temperature_2m_max",
            "temperature_2_2m_min",
            "weathercode",
            "relativehumidity_2m_max",
            "relativehumidity_2m_min"
        ],
        "timezone": "auto"
    }
    r = requests.get(url, params=params)
    return r.json()

data = fetch_bulk(lat, lon)

current = data["current_weather"]
daily = data["daily"]

# ---------------------------------------------------------
# WEATHER CODE MAPPING
# ---------------------------------------------------------
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    80: "Rain showers",
    95: "Thunderstorm",
}

def describe(code):
    return WEATHER_CODES.get(code, "Unknown")

# ---------------------------------------------------------
# CURRENT WEATHER + MAP
# ---------------------------------------------------------
col1, col2 = st.columns([1.2, 1])

with col1:
    temp = current["temperature"]
    wind = current["windspeed"]
    desc = describe(current["weathercode"])

    st.markdown(f"""
    <div class="glass">
        <div class="title">{city}</div>
        <div class="subtitle">Current conditions</div>
        <div class="value">{temp:.1f}°C</div>
        <div class="subtitle">Wind: {wind:.1f} km/h</div>
        <div class="subtitle">Weather: {desc}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="glass">
        <div class="title">Location Map</div>
        <div class="subtitle">Approximate position</div>
    </div>
    """, unsafe_allow_html=True)
    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=8)

# ---------------------------------------------------------
# FORECAST NEXT DAYS
# ---------------------------------------------------------
st.markdown("<br><h3 class='title'>Next Days Forecast</h3>", unsafe_allow_html=True)

dates = daily["time"]
tmax = daily["temperature_2m_max"]
tmin = daily["temperature_2_2m_min"]
codes = daily["weathercode"]

forecast_cols = st.columns(4)

for i in range(len(dates)):
    col = forecast_cols[i % 4]
    date = dates[i]
    dt = datetime.fromisoformat(date)
    label = dt.strftime("%a %d %b")

    desc_day = describe(codes[i])

    col.markdown(f"""
    <div class="forecast-card">
        <div class="subtitle">{label}</div>
        <div class="value" style="font-size:22px;">{tmax[i]:.1f}°C / {tmin[i]:.1f}°C</div>
        <div class="subtitle">Weather: {desc_day}</div>
    </div>
    """, unsafe_allow_html=True)
