import streamlit as st
import requests
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# ---------------------------------------------------------
# CONFIG & LIQUIDGLASS STYLE
# ---------------------------------------------------------
st.set_page_config(page_title="AstriGuardian – EarthGuardian", layout="wide")

st.markdown("""
<style>
.liquidglass {
    background: rgba(255,255,255,0.65);
    padding: 22px;
    border-radius: 25px;
    border: 1px solid rgba(255,255,255,0.35);
    backdrop-filter: blur(18px);
    box-shadow: 0 4px 25px rgba(0,0,0,0.15);
}
.metric-card {
    background: rgba(255,255,255,0.55);
    padding: 16px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.3);
    backdrop-filter: blur(14px);
    text-align: center;
}
.metric-value {
    font-size: 26px;
    font-weight: 600;
    margin-bottom: 8px;
}
.metric-label {
    font-size: 14px;
    color: #555;
    margin-bottom: 6px;
}
.metric-bar {
    width: 100%;
    height: 8px;
    border-radius: 999px;
    background: rgba(220,220,220,0.8);
    overflow: hidden;
}
.metric-bar-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #4facfe, #00f2fe);
}
.predcard {
    background: rgba(255,255,255,0.55);
    padding: 16px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.3);
    backdrop-filter: blur(14px);
    margin-right: 15px;
    min-width: 190px;
    display: inline-block;
}
.pred-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 4px;
}
.pred-emoji {
    font-size: 22px;
    margin-bottom: 6px;
}
.pred-text {
    font-size: 14px;
    color: #444;
}
</style>
""", unsafe_allow_html=True)

st.title("🛰️ AstriGuardian — EarthGuardian Dashboard")

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
st.sidebar.header("Location")
lat = st.sidebar.number_input("Latitude", value=8.98, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=-79.52, format="%.4f")
days_ahead = st.sidebar.slider("Days to predict", 1, 7, 3)

st.sidebar.write("Data: Open-Meteo (hourly weather + air quality)")

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

# ---------------------------------------------------------
# FETCH FUNCTIONS
# ---------------------------------------------------------
def fetch_weather(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": "temperature_2m,relativehumidity_2m,dewpoint_2m",
        "timezone": "auto",
    }
    r = requests.get(WEATHER_URL, params=params)
    return r.json()

def fetch_air(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "pm10,pm2_5,european_aqi",
        "timezone": "auto",
    }
    r = requests.get(AIR_URL, params=params)
    return r.json()

# ---------------------------------------------------------
# FETCH DATA
# ---------------------------------------------------------
weather = fetch_weather(lat, lon)
air = fetch_air(lat, lon)

if "hourly" not in weather or "current_weather" not in weather:
    st.error("Weather data incomplete.")
    st.json(weather)
    st.stop()

if "hourly" not in air:
    st.error("Air quality data incomplete.")
    st.json(air)
    st.stop()

hourly_weather = weather["hourly"]
current = weather["current_weather"]
hourly_air = air["hourly"]

df_temp = pd.DataFrame({
    "time": hourly_weather["time"],
    "temp": hourly_weather["temperature_2m"],
    "humidity": hourly_weather["relativehumidity_2m"],
    "dew": hourly_weather["dewpoint_2m"],
})
df_temp["date"] = df_temp["time"].str.slice(0, 10)
df_temp.set_index("time", inplace=True)

df_air = pd.DataFrame({
    "time": hourly_air["time"],
    "aqi": hourly_air["european_aqi"],
    "pm10": hourly_air["pm10"],
    "pm2_5": hourly_air["pm2_5"],
})
df_air.set_index("time", inplace=True)

# ---------------------------------------------------------
# HELPER: METRIC WIDGET WITH PROGRESS BAR
# ---------------------------------------------------------
def metric_widget(label, value, min_val, max_val):
    # normalize 0–100
    try:
        pct = (value - min_val) / (max_val - min_val)
    except ZeroDivisionError:
        pct = 0.0
    pct = max(0.0, min(1.0, pct)) * 100

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
            <div class="metric-bar">
                <div class="metric-bar-fill" style="width:{pct:.1f}%"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# TOP: MAP + CURRENT WIDGETS
# ---------------------------------------------------------
col_map, col_widgets = st.columns([1, 2])

with col_map:
    st.markdown('<div class="liquidglass">', unsafe_allow_html=True)
    st.subheader("📍 Location")
    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))
    st.markdown("</div>", unsafe_allow_html=True)

with col_widgets:
    st.markdown('<div class="liquidglass">', unsafe_allow_html=True)
    st.subheader("🌤 Current Conditions (LiquidGlass Widgets)")

    temp_val = current["temperature"]
    wind_val = current["windspeed"]
    hum_val = df_temp["humidity"].iloc[-1]
    dew_val = df_temp["dew"].iloc[-1]
    aqi_val = df_air["aqi"].iloc[-1]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_widget("Temperature (°C)", f"{temp_val:.1f}", -10, 45)
    with c2:
        metric_widget("Wind speed (m/s)", f"{wind_val:.1f}", 0, 40)
    with c3:
        metric_widget("Humidity (%)", f"{hum_val:.0f}", 0, 100)
    with c4:
        metric_widget("AQI", f"{aqi_val:.0f}", 0, 300)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# HOURLY TEMPERATURE WIDGET
# ---------------------------------------------------------
st.markdown('<div class="liquidglass">', unsafe_allow_html=True)
st.subheader("📈 Hourly Temperature")
st.line_chart(df_temp[["temp"]])
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# AIR QUALITY WIDGET
# ---------------------------------------------------------
st.markdown('<div class="liquidglass">', unsafe_allow_html=True)
st.subheader("💨 Air Quality (AQI)")
st.line_chart(df_air[["aqi"]])
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# ML PREDICTIONS
# ---------------------------------------------------------
st.markdown('<div class="liquidglass">', unsafe_allow_html=True)
st.subheader("🔮 Predictions")

df_temp_sorted = df_temp.reset_index().copy()
df_temp_sorted["t_index"] = np.arange(len(df_temp_sorted))
X = df_temp_sorted[["t_index"]].values
y = df_temp_sorted["temp"].values

future_days = []

if len(X) > 10:
    model = LinearRegression()
    model.fit(X, y)

    hours_per_day = 24
    last_index = df_temp_sorted["t_index"].iloc[-1]

    for d in range(1, days_ahead + 1):
        start = last_index + (d - 1) * hours_per_day + 1
        end = last_index + d * hours_per_day
        future_indices = np.arange(start, end).reshape(-1, 1)
        preds = model.predict(future_indices)
        min_pred = float(np.min(preds))
        max_pred = float(np.max(preds))

        # simple emoji + description
        if max_pred >= 32:
            emoji = "🔥"
            desc = "Very hot, stay hydrated."
        elif max_pred >= 26:
            emoji = "🌞"
            desc = "Warm and sunny vibes."
        elif max_pred >= 18:
            emoji = "🌤️"
            desc = "Mild and comfortable."
        else:
            emoji = "❄️"
            desc = "Cool, maybe a jacket."

        future_days.append({
            "day": d,
            "min": min_pred,
            "max": max_pred,
            "emoji": emoji,
            "desc": desc,
        })

# ---------------------------------------------------------
# HORIZONTAL PREDICTION WIDGETS
# ---------------------------------------------------------
st.write("### Upcoming Days (Scrollable Prediction Widgets)")

if future_days:
    st.markdown('<div style="white-space: nowrap; overflow-x: auto;">', unsafe_allow_html=True)

    for day in future_days:
        st.markdown(
            f"""
            <div class="predcard">
                <div class="pred-title">Day +{day['day']}</div>
                <div class="pred-emoji">{day['emoji']}</div>
                <div class="pred-text">
                    Min: {day['min']:.1f}°C<br>
                    Max: {day['max']:.1f}°C<br>
                    {day['desc']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.write("Not enough data for predictions yet.")

st.caption("AstriGuardian — LiquidGlass widgets + ML predictions using scikit-learn.")
st.markdown("</div>", unsafe_allow_html=True)
