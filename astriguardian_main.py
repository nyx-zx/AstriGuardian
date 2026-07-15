import streamlit as st
import requests
import pandas as pd

# ---------------------------------------------------------
# STREAMLIT CONFIG & LIQUIDGLASS STYLE
# ---------------------------------------------------------
st.set_page_config(page_title="AstriGuardian – EarthGuardian", layout="wide")

st.markdown("""
<style>
.liquidglass {
    background: rgba(255,255,255,0.65);
    padding: 20px;
    border-radius: 22px;
    border: 1px solid rgba(200,200,200,0.6);
    backdrop-filter: blur(18px);
}
</style>
""", unsafe_allow_html=True)

st.title("🛰️ AstriGuardian – EarthGuardian Dashboard")

# ---------------------------------------------------------
# SIDEBAR INPUTS
# ---------------------------------------------------------
st.sidebar.header("Location")
lat = st.sidebar.number_input("Latitude", value=8.98, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=-79.52, format="%.4f")

st.sidebar.write("Data source: Open-Meteo (hourly weather + air quality)")

# ---------------------------------------------------------
# API ENDPOINTS
# ---------------------------------------------------------
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

# ---------------------------------------------------------
# FETCH FUNCTIONS (HOURLY ONLY)
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

# Build hourly temp dataframe
df_temp = pd.DataFrame({
    "time": hourly_weather["time"],
    "temp": hourly_weather["temperature_2m"],
})
df_temp["date"] = df_temp["time"].str.slice(0, 10)
df_temp.set_index("time", inplace=True)

# Aggregate per day for predictions
daily_from_hourly = (
    df_temp.groupby("date")["temp"]
    .agg(["min", "max"])
    .reset_index()
)

# ---------------------------------------------------------
# MAP + CURRENT WEATHER WIDGETS
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

df_air = pd.DataFrame({
    "time": hourly_air["time"],
    "aqi": hourly_air["european_aqi"],
    "pm10": hourly_air["pm10"],
    "pm2_5": hourly_air["pm2_5"],
})
df_air.set_index("time", inplace=True)

st.line_chart(df_air[["aqi"]])
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# PREDICTIONS SECTION (WIDGETS, HORIZONTAL)
# ---------------------------------------------------------
st.markdown('<div class="liquidglass">', unsafe_allow_html=True)
st.subheader("🔮 Predictions")

if not daily_from_hourly.empty:
    # Slider to scroll through days
    day_index = st.slider(
        "Scroll through days",
        min_value=0,
        max_value=len(daily_from_hourly) - 1,
        value=0,
    )

    selected_day = daily_from_hourly.iloc[day_index]
    st.markdown("##### Selected day prediction")
    st.write(
        f"📅 **{selected_day['date']}** — "
        f"min **{selected_day['min']:.1f}°C**, "
        f"max **{selected_day['max']:.1f}°C**"
    )

    st.markdown("##### Upcoming days (widgets)")
    cols = st.columns(min(len(daily_from_hourly), 5))
    for i, row in enumerate(daily_from_hourly.itertuples()):
        if i >= len(cols):
            break
        with cols[i]:
            st.markdown("###### Day widget")
            st.write(f"📅 {row.date}")
            st.write(f"Min: {row.min:.1f}°C")
            st.write(f"Max: {row.max:.1f}°C")
else:
    st.write("No prediction data available yet.")

st.caption("AstriGuardian – predictions derived from hourly temperature data.")
st.markdown("</div>", unsafe_allow_html=True)
