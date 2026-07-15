import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import openmeteo_requests
import requests_cache
from datetime import datetime
import leafmap.foliumap as leafmap

# ---------------------------------------------------------
# STREAMLIT PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="EarthGuardian Live",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# CUSTOM LIQUID GLASS DARK CSS
# ---------------------------------------------------------
st.markdown("""
<style>

body {
    background: #0b0b0c !important;
}

[data-testid="stAppViewContainer"] {
    background: #0b0b0c;
}

.widget {
    width: 100%;
    height: 130px;
    border-radius: 26px;
    background: linear-gradient(to top right, rgba(255,255,255,0.10), rgba(255,255,255,0.03));
    backdrop-filter: blur(20px);
    box-shadow:
        inset 0 0 0 1px rgba(255,255,255,0.18),
        0 6px 16px rgba(0,0,0,0.45);
    padding: 14px;
    text-align: center;
    transition: transform .25s ease, box-shadow .25s ease;
}

.widget:hover {
    transform: translateY(-4px) scale(1.03);
    box-shadow:
        inset 0 0 0 1px rgba(255,255,255,0.25),
        0 10px 26px rgba(0,0,0,0.55);
}

.liquid-bar {
    width: 80%;
    height: 16px;
    background: rgba(255,255,255,0.18);
    border-radius: 12px;
    overflow: hidden;
    margin: auto;
    margin-top: 10px;
    position: relative;
}

.liquid-fill {
    height: 100%;
    background: linear-gradient(90deg, #4facfe, #00f2fe);
    border-radius: 12px;
    animation: liquidWave 2s infinite ease-in-out;
}

@keyframes liquidWave {
    0% { filter: brightness(1); }
    50% { filter: brightness(1.4); }
    100% { filter: brightness(1); }
}

.liquid-value {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    font-size: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #000;
    font-weight: 600;
}

.risk {
    padding: 14px;
    border-radius: 18px;
    font-size: 14px;
    text-align: center;
    backdrop-filter: blur(20px);
    font-weight: 600;
    box-shadow:
        inset 0 0 0 1px rgba(255,255,255,0.15),
        0 8px 20px rgba(0,0,0,0.4);
}

.low { background: rgba(46, 204, 113, 0.25); }
.moderate { background: rgba(230, 195, 0, 0.25); }
.high { background: rgba(230, 126, 34, 0.25); }
.critical { background: rgba(231, 76, 60, 0.25); }

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# OPEN-METEO CLIENT
# ---------------------------------------------------------
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
openmeteo = openmeteo_requests.Client(session=cache_session)

# ---------------------------------------------------------
# COORDINATES
# ---------------------------------------------------------
coords = {
    "Panamá": (9.0, -79.5),
    "Panamá Oeste": (8.9, -79.8),
    "Colón": (9.35, -79.9),
    "Chiriquí": (8.4, -82.4),
    "Veraguas": (8.1, -80.9),
    "Coclé": (8.6, -80.4),
    "Herrera": (7.8, -80.3),
    "Los Santos": (7.5, -80.4),
    "Darién": (8.0, -77.5),
    "Bocas del Toro": (9.35, -82.25)
}

# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------
st.markdown("<h1 style='text-align:center;'>EARTHGUARDIAN LIVE — Panamá</h1>", unsafe_allow_html=True)

# ---------------------------------------------------------
# SELECT PROVINCE
# ---------------------------------------------------------
province = st.selectbox("Selecciona provincia:", list(coords.keys()))
lat, lon = coords[province]

# ---------------------------------------------------------
# SAFE FETCH WITH SESSION STATE FALLBACK
# ---------------------------------------------------------
def safe_fetch(name, url, params):
    try:
        response = openmeteo.weather_api(url, params=params)
        data = response.json()
        st.session_state[name] = data
        return data
    except Exception:
        st.warning(f"⚠ API limit reached — using cached {name} data.")
        return st.session_state.get(name)

# ---------------------------------------------------------
# FETCH WEATHER SAFELY
# ---------------------------------------------------------
weather = safe_fetch(
    "weather",
    "https://api.open-meteo.com/v1/forecast",
    {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["temperature_2m", "relativehumidity_2m", "precipitation", "wind_speed_10m", "uv_index"],
        "current_weather": True,
        "timezone": "auto"
    }
)

air = safe_fetch(
    "air",
    "https://air-quality-api.open-meteo.com/v1/air-quality",
    {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide", "ozone"],
        "timezone": "auto"
    }
)

# ---------------------------------------------------------
# EXTRACT DATA
# ---------------------------------------------------------
current = weather["current_weather"]
hourly = weather["hourly"]
air_hourly = air["hourly"]

# ---------------------------------------------------------
# WIDGET FUNCTION
# ---------------------------------------------------------
def widget(label, value, percent):
    return f"""
    <div class="widget">
        <h4>{label}</h4>
        <div class="liquid-bar">
            <div class="liquid-fill" style="width:{percent}%"></div>
            <div class="liquid-value">{value}</div>
        </div>
    </div>
    """

# ---------------------------------------------------------
# WIDGETS ROW
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.markdown(widget("Temperatura", f"{current['temperature']}°C", current['temperature'] * 2), unsafe_allow_html=True)
col2.markdown(widget("Humedad", f"{hourly['relativehumidity_2m'][0]}%", hourly['relativehumidity_2m'][0]), unsafe_allow_html=True)
col3.markdown(widget("Lluvia", f"{hourly['precipitation'][0]} mm", hourly['precipitation'][0] * 10), unsafe_allow_html=True)
col4.markdown(widget("Viento", f"{current['windspeed']} km/h", current['windspeed'] * 3), unsafe_allow_html=True)

col5, col6, col7, col8 = st.columns(4)

col5.markdown(widget("UV", f"{hourly['uv_index'][0]}", hourly['uv_index'][0] * 10), unsafe_allow_html=True)
col6.markdown(widget("PM2.5", f"{air_hourly['pm2_5'][0]} µg/m³", air_hourly['pm2_5'][0] * 2), unsafe_allow_html=True)

rain_next = hourly["precipitation"][1:4]
will_rain = any(v > 0.5 for v in rain_next)

col7.markdown(widget("Predicción", "Lluvia pronto" if will_rain else "Sin lluvia", 100 if will_rain else 20), unsafe_allow_html=True)
col8.markdown(widget("Hora", datetime.now().strftime("%H:%M"), 50), unsafe_allow_html=True)

# ---------------------------------------------------------
# RISK CALCULATION
# ---------------------------------------------------------
def risk_percent(value, maxv):
    return min(100, int((value / maxv) * 100))

fire_risk = risk_percent(current["temperature"] + current["windspeed"], 100)
flood_risk = risk_percent(hourly["precipitation"][0], 50)
heat_risk = risk_percent(current["temperature"] + hourly["relativehumidity_2m"][0], 120)
air_risk = risk_percent(air_hourly["pm2_5"][0], 100)

# ---------------------------------------------------------
# RISK BLOCKS
# ---------------------------------------------------------
st.markdown("### Riesgos Ambientales")

risk_cols = st.columns(4)

def risk_block(title, percent):
    level = "low"
    if percent > 60: level = "high"
    elif percent > 30: level = "moderate"
    return f"<div class='risk {level}'>{title}: {percent}%</div>"

risk_cols[0].markdown(risk_block("Incendio", fire_risk), unsafe_allow_html=True)
risk_cols[1].markdown(risk_block("Inundación", flood_risk), unsafe_allow_html=True)
risk_cols[2].markdown(risk_block("Ola de calor", heat_risk), unsafe_allow_html=True)
risk_cols[3].markdown(risk_block("Calidad del aire", air_risk), unsafe_allow_html=True)

# ---------------------------------------------------------
# RECOMMENDATIONS
# ---------------------------------------------------------
recs = []

if fire_risk > 60: recs.append("Evita quemas y mantén vigilancia en áreas secas.")
if flood_risk > 60: recs.append("Revisa drenajes y evita zonas bajas.")
if heat_risk > 60: recs.append("Prende el aire acondicionado y mantente hidratado.")
if air_risk > 60: recs.append("Evita actividades al aire libre si tienes alergias.")

st.markdown("### Recomendaciones")
st.markdown("<div class='risk'>" + "<br>".join(recs if recs else ["Condiciones estables."]) + "</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# CHART + MAP SIDE BY SIDE
# ---------------------------------------------------------
chart_col, map_col = st.columns([1, 1])

# CHART
df = pd.DataFrame({
    "time": hourly["time"][:6],
    "temp": hourly["temperature_2m"][:6],
    "humidity": hourly["relativehumidity_2m"][:6],
    "rain": hourly["precipitation"][:6],
    "wind": hourly["wind_speed_10m"][:6],
    "uv": hourly["uv_index"][:6],
    "pm25": air_hourly["pm2_5"][:6]
})

fig = go.Figure()

fig.add_trace(go.Scatter(x=df["time"], y=df["temp"], mode="lines", name="Temp °C", line=dict(color="#ff4d4d")))
fig.add_trace(go.Scatter(x=df["time"], y=df["humidity"], mode="lines", name="Humedad %", line=dict(color="#4da6ff")))
fig.add_trace(go.Scatter(x=df["time"], y=df["rain"], mode="lines", name="Lluvia mm", line=dict(color="#7a5cff")))
fig.add_trace(go.Scatter(x=df["time"], y=df["wind"], mode="lines", name="Viento km/h", line=dict(color="#33cc33")))
fig.add_trace(go.Scatter(x=df["time"], y=df["uv"], mode="lines", name="UV", line=dict(color="#ffcc00")))
fig.add_trace(go.Scatter(x=df["time"], y=df["pm25"], mode="lines", name="PM2.5", line=dict(color="#cccccc")))

fig.update_layout(
    height=300,
    paper_bgcolor="#0b0b0c",
    plot_bgcolor="#0b0b0c",
    font=dict(color="white")
)

chart_col.plotly_chart(fig, use_container_width=True)

# MAP
m = leafmap.Map(center=(lat, lon), zoom=8)
m.add_marker(location=(lat, lon), popup=province)
map_col.write(m.to_streamlit(height=300))
