import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="EarthGuardian", layout="wide")

# -------------------------------
# LIQUID GLASS WHITE CSS
# -------------------------------
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
    box-shadow: 0 18px 40px rgba(15,23,42,0.18), inset 0 0 0 1px rgba(255,255,255,0.7);
    padding: 20px;
    transition: 0.25s;
}
.glass:hover {
    transform: translateY(-4px);
    box-shadow: 0 24px 60px rgba(15,23,42,0.25), inset 0 0 0 1px rgba(255,255,255,0.9);
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
    box-shadow: 0 14px 32px rgba(15,23,42,0.16), inset 0 0 0 1px rgba(255,255,255,0.8);
    padding: 14px 16px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# CITY LIST
# -------------------------------
CITIES = {
    "Panamá, Panamá": (9.0, -79.5),
    "Colón": (9.35, -79.9),
    "David": (8.43, -82.43),
    "Santiago": (8.1, -80.97),
    "Chitré": (7.96, -80.43)
}

st.markdown("<h1 class='title' style='text-align:center;'>EarthGuardian — Liquid Glass Forecast</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle' style='text-align:center;'>Modern weather dashboard with forecast and map</p>", unsafe_allow_html=True)

city = st.selectbox("Choose a city", list(CITIES.keys()))
lat, lon = CITIES[city]

# -------------------------------
# SAFE DAILY FORECAST (NO RATE LIMITS)
# -------------------------------
@st.cache_data(ttl=3600)
def fetch_daily(lat, lon):
    today = datetime.utcnow().date()
    start = today - timedelta(days=1)
    end = today + timedelta(days=5)

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "weathercode",
            "relativehumidity_2m_max",
            "relativehumidity_2m_min"
        ],
        "timezone": "auto"
    }
    r = requests.get(url, params=params)
    return r.json()

data = fetch_daily(lat, lon)
daily = data["daily"]

# -------------------------------
# WEATHER CODE MAPPING
# -------------------------------
CODES = {
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
    95: "Thunderstorm"
}

def describe(code):
    return CODES.get(code, "Unknown")

# -------------------------------
# CURRENT WEATHER (approx)
# -------------------------------
today = str(datetime.utcnow().date())
idx = daily["time"].index(today)

temp_max = daily["temperature_2m_max"][idx]
temp_min = daily["temperature_2m_min"][idx]
hum_max = daily["relativehumidity_2m_max"][idx]
hum_min = daily["relativehumidity_2m_min"][idx]
code = daily["weathercode"][idx]

current_temp = (temp_max + temp_min) / 2
current_hum = (hum_max + hum_min) / 2
current_desc = describe(code)

# -------------------------------
# HTML RENDERING
# -------------------------------
html = f"""
<div class="glass">
    <div class="title">{city}</div>
    <div class="subtitle">Current conditions</div>
    <div class="value">{current_temp:.1f}°C</div>
    <div class="subtitle">Humidity: {current_hum:.0f}%</div>
    <div class="subtitle">Weather: {current_desc}</div>
</div>
"""

st.markdown(html, unsafe_allow_html=True)

# -------------------------------
# MAP
# -------------------------------
st.markdown("<br>", unsafe_allow_html=True)
st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=8)

# -------------------------------
# FORECAST
# -------------------------------
st.markdown("<br><h3 class='title'>Next Days Forecast</h3>", unsafe_allow_html=True)

dates = daily["time"]
tmax = daily["temperature_2m_max"]
tmin = daily["temperature_2m_min"]
codes = daily["weathercode"]

cols = st.columns(4)

for i in range(len(dates)):
    col = cols[i % 4]
    dt = datetime.fromisoformat(dates[i])
    label = dt.strftime("%a %d %b")
    desc = describe(codes[i])

    card = f"""
    <div class="forecast-card">
        <div class="subtitle">{label}</div>
        <div class="value" style="font-size:22px;">{tmax[i]:.1f}°C / {tmin[i]:.1f}°C</div>
        <div class="subtitle">Weather: {desc}</div>
    </div>
    """
    col.markdown(card, unsafe_allow_html=True)
