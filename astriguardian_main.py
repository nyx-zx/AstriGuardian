import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# ---------------------------------------------------------
# STREAMLIT PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="EarthGuardian Forecast",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# CUSTOM WHITE LIQUID GLASS CSS
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

.glass-card {
    width: 100%;
    border-radius: 24px;
    background: linear-gradient(to top right, rgba(255,255,255,0.85), rgba(255,255,255,0.65));
    backdrop-filter: blur(22px);
    box-shadow:
        0 18px 40px rgba(15, 23, 42, 0.18),
        inset 0 0 0 1px rgba(255,255,255,0.7);
    padding: 18px 20px;
    transition: transform .25s ease, box-shadow .25s ease;
}

.glass-card:hover {
    transform: translateY(-4px);
    box-shadow:
        0 24px 60px rgba(15, 23, 42, 0.25),
        inset 0 0 0 1px rgba(255,255,255,0.9);
}

.glass-title {
    font-size: 18px;
    font-weight: 600;
    color: #111827;
    margin-bottom: 4px;
}

.glass-sub {
    font-size: 13px;
    color: #6b7280;
}

.glass-value {
    font-size: 26px;
    font-weight: 700;
    color: #111827;
    margin-top: 8px;
}

.glass-chip {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
    background: linear-gradient(to top right, #4f46e5, #6366f1);
    color: #f9fafb;
    box-shadow: 0 8px 18px rgba(79,70,229,0.35);
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
    transition: transform .2s ease, box-shadow .2s ease;
}

.forecast-card:hover {
    transform: translateY(-3px);
    box-shadow:
        0 20px 40px rgba(15, 23, 42, 0.22),
        inset 0 0 0 1px rgba(255,255,255,0.95);
}

.forecast-day {
    font-size: 14px;
    font-weight: 600;
    color: #111827;
}

.forecast-temp {
    font-size: 18px;
    font-weight: 700;
    color: #1f2937;
}

.forecast-meta {
    font-size: 12px;
    color: #6b7280;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIMPLE CITY COORDS
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
st.markdown(
    "<h1 style='text-align:center; color:#111827;'>EarthGuardian — Liquid Glass Forecast</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center; color:#6b7280;'>Live temperature, humidity and multi‑day forecast with a modern glass UI.</p>",
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# CITY SELECT
# ---------------------------------------------------------
city = st.selectbox("Choose location", list(CITIES.keys()))
lat, lon = CITIES[city]

# ---------------------------------------------------------
# OPEN-METEO FORECAST (HTTP, NO CLIENT)
# ---------------------------------------------------------
@st.cache_data(ttl=900)
def fetch_forecast(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": ["temperature_2m", "relativehumidity_2m"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "relativehumidity_2m_max", "relativehumidity_2m_min", "weathercode"],
        "timezone": "auto"
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

data = fetch_forecast(lat, lon)

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
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Rain showers",
    81: "Moderate showers",
    82: "Violent showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

def describe_code(code):
    return WEATHER_CODES.get(code, "Unknown")

# ---------------------------------------------------------
# TOP ROW: CURRENT CONDITIONS + MAP
# ---------------------------------------------------------
top_left, top_right = st.columns([1.2, 1])

with top_left:
    temp = current["temperature"]
    wind = current["windspeed"]
    time_str = current["time"]

    st.markdown(
        f"""
        <div class="glass-card">
            <div class="glass-title">{city}</div>
            <div class="glass-sub">Live conditions • {time_str}</div>
            <div style="margin-top:10px;">
                <span class="glass-chip">Current weather</span>
            </div>
            <div class="glass-value" style="margin-top:14px;">{temp:.1f}°C</div>
            <div class="glass-sub" style="margin-top:4px;">
                Wind: {wind:.1f} km/h • Code: {current['weathercode']}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Quick humidity snapshot from hourly
    hourly_times = data["hourly"]["time"]
    hourly_temps = data["hourly"]["temperature_2m"]
    hourly_hums = data["hourly"]["relativehumidity_2m"]

    # Take the first hour as "current-ish" humidity
    if hourly_hums:
        hum_now = hourly_hums[0]
    else:
        hum_now = None

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="glass-card">
            <div class="glass-title">Humidity snapshot</div>
            <div class="glass-sub">Approximate current humidity</div>
            <div class="glass-value" style="margin-top:10px;">{hum_now if hum_now is not None else 'N/A'}%</div>
            <div class="glass-sub" style="margin-top:4px;">
                Based on latest hourly data from Open‑Meteo.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with top_right:
    st.markdown(
        """
        <div class="glass-card">
            <div class="glass-title">Location map</div>
            <div class="glass-sub">Approximate position of the selected city.</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.map(
        pd.DataFrame(
            {"lat": [lat], "lon": [lon]}
        ),
        zoom=8
    )

# ---------------------------------------------------------
# DAILY FORECAST SECTION
# ---------------------------------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='color:#111827;'>Multi‑day forecast</h3>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='color:#6b7280;'>Predicted temperature, humidity and weather for the next days.</p>",
    unsafe_allow_html=True
)

dates = daily["time"]
tmax = daily["temperature_2m_max"]
tmin = daily["temperature_2m_min"]
hmax = daily["relativehumidity_2m_max"]
hmin = daily["relativehumidity_2m_min"]
codes = daily["weathercode"]

# Build forecast cards
forecast_cols = st.columns(4)

for i in range(min(len(dates), 8)):  # up to 8 days
    col = forecast_cols[i % 4]
    day = dates[i]
    dt = datetime.fromisoformat(day)
    label = dt.strftime("%a %d %b")

    temp_hi = tmax[i]
    temp_lo = tmin[i]
    hum_hi = hmax[i]
    hum_lo = hmin[i]
    code = codes[i]
    desc = describe_code(code)

    col.markdown(
        f"""
        <div class="forecast-card">
            <div class="forecast-day">{label}</div>
            <div class="forecast-temp" style="margin-top:6px;">
                {temp_hi:.1f}°C / {temp_lo:.1f}°C
            </div>
            <div class="forecast-meta" style="margin-top:4px;">
                Humidity: {hum_lo:.0f}% – {hum_hi:.0f}%<br>
                Weather: {desc} (code {code})
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# SUMMARY / HINTS
# ---------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    """
    <div class="glass-card">
        <div class="glass-title">Summary & hints</div>
        <div class="glass-sub" style="margin-top:6px;">
            • Use the forecast cards to plan outdoor activities.<br>
            • Watch for high humidity + high temperature days (heat stress).<br>
            • Clear sky codes (0–1) are best for visibility and comfort.<br>
            • Rain / thunderstorm codes (61+ / 95+) suggest caution outdoors.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
