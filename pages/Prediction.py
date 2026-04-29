


import streamlit as st
import pandas as pd
import numpy as np
import requests
import schedule
import threading
import time
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# =========================================
# PAGE CONFIG
# =========================================
st.set_page_config(
    page_title="Prediction",
    layout="wide"
)

# =========================================
# SESSION STATE INIT
# Keeps AQI data alive across all reruns
# =========================================
if "aqi_data" not in st.session_state:
    st.session_state.aqi_data = None

# =========================================
# API KEYS
# =========================================

API = os.getenv("AQICN_API_KEY")
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# =========================================
# GLOBAL CSS
# =========================================
st.markdown("""
<style>
[data-testid="stSidebarNav"] ul li:first-child { display:none; }

.stApp { background:white; }

.solution{
    background:white; padding:15px; border-radius:12px;
    text-align:center; color:#111827; font-weight:600;
    min-height:90px; display:flex; align-items:center;
    justify-content:center; box-shadow:0 2px 8px rgba(0,0,0,.08);
}

.health{
    background:linear-gradient(135deg,#1e293b,#0f172a);
    padding:20px; border-radius:15px; text-align:center; color:white;
}

.metric-box{
    background:#f5f7fb; padding:25px; border-radius:18px;
    box-shadow:0 2px 8px rgba(0,0,0,.08); text-align:center;
    margin-bottom:20px; border-left:6px solid #22c55e;
}

.metric-name  { font-size:20px; font-weight:600; color:#111827; }
.metric-value { font-size:34px; font-weight:bold; margin-top:10px; color:#1e293b; }

.risk-box{
    padding:22px; border-radius:16px; text-align:center;
    font-weight:700; font-size:22px; margin-bottom:10px;
}

.forecast-card{
    background:#f5f7fb; padding:14px; border-radius:12px;
    text-align:center; box-shadow:0 2px 6px rgba(0,0,0,.07);
}

.activity-card{
    background:#f0fdf4; border-left:5px solid #22c55e;
    padding:16px; border-radius:12px; margin-bottom:10px;
    font-weight:600;
}

.activity-warn{
    background:#fff7ed; border-left:5px solid #f97316;
    padding:16px; border-radius:12px; margin-bottom:10px;
    font-weight:600;
}

.section-header{
    font-size:26px; font-weight:700; margin-bottom:6px; color:#1e293b;
}

.sidebar-feature-info{
    background:#f1f5f9; padding:14px; border-radius:12px;
    font-size:13px; color:#475569; margin-top:10px; line-height:1.6;
}
</style>
""", unsafe_allow_html=True)


# =========================================
# FETCH AQI
# =========================================
def fetch(city):
    url = f"https://api.waqi.info/feed/{city}/?token={API}"
    res = requests.get(url).json()
    if res["status"] != "ok":
        return None, None
    iaqi = res["data"]["iaqi"]
    raw = {
        "PM2.5": iaqi.get("pm25", {}).get("v"),
        "PM10":  iaqi.get("pm10", {}).get("v"),
        "NO2":   iaqi.get("no2",  {}).get("v"),
        "SO2":   iaqi.get("so2",  {}).get("v"),
        "CO":    iaqi.get("co",   {}).get("v"),
        "O3":    iaqi.get("o3",   {}).get("v"),
    }
    vals = [v for v in raw.values() if v is not None]
    if not vals:
        return None, None
    missing = sum(1 for v in raw.values() if v is None)
    return raw, missing


# =========================================
# FETCH WEATHER
# =========================================
def fetch_weather(city):
    url = (f"https://api.openweathermap.org/data/2.5/weather"
           f"?q={city}&appid={OPENWEATHER_KEY}&units=metric")
    try:
        res = requests.get(url, timeout=10).json()
        if str(res.get("cod")) != "200":
            return None
        return {
            "temp":      res["main"]["temp"],
            "humidity":  res["main"]["humidity"],
            "wind":      res["wind"]["speed"],
            "condition": res["weather"][0]["main"]
        }
    except:
        return None


# =========================================
# TELEGRAM ALERT
# =========================================
def send_daily_alert():
    city = "Delhi"
    raw, _ = fetch(city)
    if not raw:
        return
    aqi = int(max(v for v in raw.values() if v is not None))
    advice = ("Air moderate. Outdoor okay." if aqi <= 100
              else "Avoid jogging 8-10 AM." if aqi <= 200
              else "Poor AQI. Stay cautious.")
    msg = f"Daily AQI Forecast 🌫️\nCity: {city}\nAQI: {aqi}\n\nAdvice:\n{advice}"
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                  data={"chat_id": CHAT_ID, "text": msg})


# =========================================
# AQI HELPERS
# =========================================
def category(aqi):
    if aqi <= 50:    return "GOOD",         "#ffffff", "#00e600"
    elif aqi <= 100: return "SATISFACTORY",  "#111827", "#9acd32"
    elif aqi <= 200: return "MODERATE",      "#111827", "#fff000"
    elif aqi <= 300: return "POOR",          "#ffffff", "#ff8800"
    elif aqi <= 400: return "VERY POOR",     "#ffffff", "#ff1a1a"
    else:            return "SEVERE",        "#ffffff", "#8b0029"

def solutions(aqi):
    if aqi <= 50:
        return ["🌿 Outdoor activity safe","🏠 Ventilate home",
                "💧 Stay hydrated","🏃 Exercise recommended"]
    elif aqi <= 100:
        return ["😷 Mask if sensitive","🚶 Limit long exposure",
                "🪟 Keep windows closed","💧 Hydrate"]
    elif aqi <= 200:
        return ["😷 Wear N95","🏃 Avoid workouts outside",
                "🧴 Use purifier","🚗 Reduce traffic exposure"]
    elif aqi <= 300:
        return ["🏠 Stay indoors","🧴 Purifier continuously",
                "❌ Avoid exertion","😷 Mask outside"]
    else:
        return ["🚨 Strict indoor stay","😷 N95/N99 mask",
                "❌ Avoid exertion","👨‍👩‍👧 Protect elderly"]

def health(aqi):
    if aqi <= 50:
        return ["No major respiratory issues","Very low heart stress","Minimal allergies"]
    elif aqi <= 100:
        return ["Mild irritation possible","Sensitive groups discomfort","Minor allergies possible"]
    elif aqi <= 200:
        return ["Breathing discomfort","Asthma symptoms possible","Fatigue possible"]
    elif aqi <= 300:
        return ["High asthma risk","Heart patients affected","Persistent coughing"]
    else:
        return ["Severe respiratory distress","Serious heart strain","Dangerous for all"]


# =========================================
# FEATURE 1 HELPERS — Personalized Risk
# =========================================
def personal_risk_score(aqi, age, has_asthma, has_heart):
    base = 0
    if aqi <= 50:    base = 5
    elif aqi <= 100: base = 20
    elif aqi <= 200: base = 40
    elif aqi <= 300: base = 55
    else:            base = 65

    age_bonus = 0
    if age < 12 or age >= 65: age_bonus = 15
    elif age >= 50:            age_bonus = 8

    asthma_bonus = 12 if has_asthma else 0
    heart_bonus  = 10 if has_heart  else 0

    score = min(100, base + age_bonus + asthma_bonus + heart_bonus)

    if score <= 20:
        label   = "🟢 Low Risk"
        color   = "#16a34a"
        bgcolor = "#dcfce7"
        advice  = [
            "✅ Air quality is safe for your profile.",
            "🏃 You can do normal outdoor activities.",
            "💧 Stay hydrated and enjoy fresh air.",
        ]
    elif score <= 45:
        label   = "🟡 Moderate Risk"
        color   = "#ca8a04"
        bgcolor = "#fef9c3"
        advice  = [
            "⚠️ Limit prolonged outdoor exposure.",
            "😷 Carry your inhaler if you have one.",
            "🪟 Keep windows closed during peak hours.",
        ]
    elif score <= 70:
        label   = "🟠 High Risk"
        color   = "#ea580c"
        bgcolor = "#fff7ed"
        advice  = [
            "🚫 Avoid all non-essential outdoor activity.",
            "😷 Wear N95 mask if going outside.",
            "🧴 Run air purifier indoors continuously.",
            "💊 Keep medications accessible.",
        ]
    else:
        label   = "🔴 Very High Risk"
        color   = "#dc2626"
        bgcolor = "#fef2f2"
        advice  = [
            "🚨 Stay strictly indoors.",
            "😷 Wear N95/N99 even indoors if possible.",
            "🏥 Seek medical advice if any breathing difficulty.",
            "👨‍👩‍👧 Especially dangerous for your age/condition.",
        ]

    return score, label, color, bgcolor, advice, age_bonus, asthma_bonus, heart_bonus


# =========================================
# FEATURE 2 HELPERS — 7-Day Forecast
# =========================================
def generate_forecast(current_aqi, city):
    np.random.seed(abs(hash(city)) % (2**31))
    forecast = []
    aqi = current_aqi
    for i in range(7):
        date  = (datetime.today() + timedelta(days=i)).strftime("%a\n%d %b")
        drift = np.random.uniform(-0.15, 0.15) * aqi
        aqi   = max(10, min(500, aqi + drift))
        forecast.append({"date": date, "aqi": round(aqi, 1)})
    return forecast

def worst_day(forecast):
    return max(forecast, key=lambda x: x["aqi"])

def best_day(forecast):
    return min(forecast, key=lambda x: x["aqi"])

def forecast_color(aqi):
    if aqi <= 50:    return "#00e600"
    elif aqi <= 100: return "#9acd32"
    elif aqi <= 200: return "#fbbf24"
    elif aqi <= 300: return "#f97316"
    elif aqi <= 400: return "#ef4444"
    else:            return "#7f1d1d"


# =========================================
# FEATURE 3 HELPERS — Activity Planner
# =========================================
ACTIVITY_LIMITS = {
    "🏃 Jogging / Running":   {"safe": 100, "risky": 200},
    "🚴 Cycling":             {"safe": 100, "risky": 200},
    "🧓 Elderly Walking":     {"safe":  50, "risky": 100},
    "👦 Kids Outdoor Play":   {"safe":  50, "risky": 100},
    "🧘 Yoga / Stretching":   {"safe": 150, "risky": 250},
    "🏋️ Intense Gym Outdoor": {"safe":  75, "risky": 150},
}

def activity_advice(aqi, activity):
    key    = activity
    limits = ACTIVITY_LIMITS.get(key, {"safe": 100, "risky": 200})
    name   = activity.split(" ", 1)[1] if " " in activity else activity
    if aqi <= limits["safe"]:
        return "safe",     f"✅ Safe to do **{name}** right now!"
    elif aqi <= limits["risky"]:
        return "moderate", f"⚠️ Moderate risk for **{name}**. Consider wearing a mask."
    else:
        return "unsafe",   f"🚫 **{name}** is not recommended outdoors today."

def best_time_message(aqi):
    if aqi <= 100:   return "🕕 Any time is fine. Morning (6–8 AM) is typically freshest."
    elif aqi <= 200: return "🕔 Prefer early morning (5–7 AM) before traffic peaks."
    else:            return "🚫 No outdoor time recommended today. Stay indoors."

def hourly_heatmap(aqi):
    """Returns list of (hour_label, relative_aqi) for 24 hours."""
    hours = []
    for h in range(24):
        # Traffic rush hours are worse
        if 7 <= h <= 10 or 17 <= h <= 20:
            factor = 1.3
        elif 1 <= h <= 5:
            factor = 0.75
        else:
            factor = 1.0
        hours.append({
            "Hour": f"{h:02d}:00",
            "Est. AQI": round(aqi * factor)
        })
    return hours


# =========================================
# SIDEBAR — Navigation
# =========================================
st.sidebar.markdown("""
<style>
.aqi-box{
    background:#f3f4f6; padding:20px; border-radius:18px;
    box-shadow:0 2px 8px rgba(0,0,0,.08);
}
.aqi-title{ font-size:22px; font-weight:bold; margin-bottom:14px; }
.aqi-tag{
    padding:10px 14px; border-radius:8px; font-weight:600;
    margin-bottom:6px; color:white;
}
.good         { background:#00e600; }
.satisfactory { background:#9acd32; color:black !important; }
.moderate     { background:#fff000; color:black !important; }
.poor         { background:#ff8800; }
.verypoor     { background:#ff1a1a; }
.severe       { background:#8b0029; }
</style>

<div class="aqi-box">
<div class="aqi-title">🎨 AQI Scale</div>
<div class="aqi-tag good">🙂 Good (0–50)</div>
<div class="aqi-tag satisfactory">🙂 Satisfactory (51–100)</div>
<div class="aqi-tag moderate">😐 Moderate (101–200)</div>
<div class="aqi-tag poor">😷 Poor (201–300)</div>
<div class="aqi-tag verypoor">🤢 Very Poor (301–400)</div>
<div class="aqi-tag severe">☠️ Severe (401+)</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔧 Features")

# Radio acts as sidebar navigation for the 3 features
feature = st.sidebar.radio(
    "Select a feature to explore:",
    options=[
        "📊 AQI Monitor",
        "👤 Personalized Health Risk",
        "📅 7-Day AQI Forecast",
        "🏃 Outdoor Activity Planner",
    ],
    key="sidebar_feature"
)

# Feature descriptions shown in sidebar
descriptions = {
    "📊 AQI Monitor": "Enter a city to get live AQI, pollutant breakdown, health advice, and weather.",
    "👤 Personalized Health Risk": "Enter your age & health conditions to get a custom 0–100 risk score with detailed advice.",
    "📅 7-Day AQI Forecast": "See a simulated 7-day AQI trend with worst/best day alerts and improving/worsening direction.",
    "🏃 Outdoor Activity Planner": "Pick your activity (jogging, cycling, etc.) to see if today's AQI is safe + best time to go.",
}
st.sidebar.markdown(
    f'<div class="sidebar-feature-info">ℹ️ {descriptions[feature]}</div>',
    unsafe_allow_html=True
)

# =========================================
# SIDEBAR — TELEGRAM ALERT BUTTON
# =========================================
st.sidebar.markdown("---")
st.sidebar.markdown("### 📲 Telegram Alerts")
st.sidebar.caption("Get instant AQI alert + daily updates at 8 AM on Telegram.")

# Session flag so we only show the button once per session
if "telegram_subscribed" not in st.session_state:
    st.session_state.telegram_subscribed = False

def build_telegram_message(city_name, aqi_val, raw_data, weather_data):
    """Builds a rich Telegram message with current AQI data."""
    import pytz
    from datetime import datetime
    IST      = pytz.timezone("Asia/Kolkata")
    now_ist  = datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST")

    # Category
    if aqi_val <= 50:    cat_label, cat_emoji = "Good ✅",          "🟢"
    elif aqi_val <= 100: cat_label, cat_emoji = "Satisfactory 🙂",  "🟡"
    elif aqi_val <= 200: cat_label, cat_emoji = "Moderate 😐",       "🟠"
    elif aqi_val <= 300: cat_label, cat_emoji = "Poor 😷",           "🔴"
    elif aqi_val <= 400: cat_label, cat_emoji = "Very Poor 🤢",      "🔴"
    else:                cat_label, cat_emoji = "Severe ☠️",         "⚫"

    # Advice
    if aqi_val <= 50:
        advice = ["✅ Air is clean. Enjoy outdoor activities.", "💧 Stay hydrated."]
    elif aqi_val <= 100:
        advice = ["😷 Sensitive groups wear a mask.", "🚶 Limit long outdoor stays."]
    elif aqi_val <= 200:
        advice = ["😷 Wear N95 mask outdoors.", "🏃 Avoid jogging 8–10 AM.", "🧴 Use air purifier."]
    elif aqi_val <= 300:
        advice = ["🏠 Stay indoors.", "😷 N95/N99 mask if going out.", "❌ Avoid outdoor exercise."]
    else:
        advice = ["🚨 Stay strictly indoors.", "😷 N99 mask even indoors.", "🏥 Seek help if breathing issues."]

    # Best time
    if aqi_val <= 100:   outdoor_time = "🕕 Any time is fine. Morning (6–8 AM) is freshest."
    elif aqi_val <= 200: outdoor_time = "🕔 Early morning (5–7 AM) before traffic peaks."
    else:                outdoor_time = "🚫 Not recommended to go outside today."

    # Pollutants
    pollutant_lines = ""
    if raw_data:
        for k, v in raw_data.items():
            if v is not None:
                pollutant_lines += f"  • {k}: {v}\n"

    # Weather
    weather_lines = ""
    if weather_data:
        weather_lines = (
            f"\n☁️ *Weather in {city_name}*\n"
            f"  🌡 Temp: {weather_data['temp']}°C\n"
            f"  💧 Humidity: {weather_data['humidity']}%\n"
            f"  🌬 Wind: {weather_data['wind']} m/s\n"
            f"  ⛅ Condition: {weather_data['condition']}\n"
        )

    msg = f"""🌫️ *AQI Alert — {city_name.upper()}*
📅 {now_ist}
{'─' * 28}

{cat_emoji} *AQI: {aqi_val}* — {cat_label}

💡 *Advice:*
""" + "\n".join(f"  {t}" for t in advice) + f"""

⏰ *Best Outdoor Time:*
  {outdoor_time}

🔬 *Pollutants:*
{pollutant_lines}{weather_lines}
{'─' * 28}
🔔 _You will now receive this alert daily at 8:00 AM IST._
_Powered by AQI Monitor App_"""

    return msg


def send_telegram_alert(city_name, aqi_val, raw_data, weather_data):
    """Sends the alert message via Telegram Bot API."""
    msg = build_telegram_message(city_name, aqi_val, raw_data, weather_data)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        res = requests.post(url, data={
            "chat_id":    CHAT_ID,
            "text":       msg,
            "parse_mode": "Markdown",
        }, timeout=15)
        return res.status_code == 200, res.text
    except Exception as e:
        return False, str(e)


# Show button only if AQI data is available
if st.session_state.aqi_data is not None:
    if not st.session_state.telegram_subscribed:
        if st.sidebar.button(
            "📩 Send Alert & Subscribe to Daily Updates",
            use_container_width=True,
            type="primary"
        ):
            with st.sidebar:
                with st.spinner("Sending alert to Telegram..."):
                    ok, err = send_telegram_alert(
                        st.session_state.aqi_data["city"],
                        st.session_state.aqi_data["aqi"],
                        st.session_state.aqi_data["raw"],
                        st.session_state.aqi_data["weather"],
                    )
            if ok:
                st.session_state.telegram_subscribed = True
                st.sidebar.success("✅ Alert sent! Opening Telegram...")
                # Auto-open Telegram after 1 second
                st.sidebar.markdown(
                    """
                    <script>
                    setTimeout(function(){
                        window.open('https://t.me/aqi_alert_2026_bot', '_blank');
                    }, 800);
                    </script>
                    """,
                    unsafe_allow_html=True
                )
                # Fallback clickable link
                st.sidebar.markdown(
                    "👉 [Open Telegram Bot](https://t.me/aqi_alert_2026_bot)",
                    unsafe_allow_html=True
                )
            else:
                st.sidebar.error(f"❌ Failed to send. Check bot token.\n{err}")
    else:
        # Already subscribed — show status
        st.sidebar.markdown("""
        <div style='background:#dcfce7;padding:12px;border-radius:10px;
        border-left:4px solid #16a34a;font-size:13px;color:#166534;'>
            ✅ <b>Subscribed!</b><br>
            You'll receive daily AQI alerts at<br>
            <b>8:00 AM IST</b> on Telegram.
        </div>
        """, unsafe_allow_html=True)
        st.sidebar.markdown(
            "👉 [Open Telegram Bot](https://t.me/aqi_alert_2026_bot)",
            unsafe_allow_html=True
        )
        # Allow unsubscribe
        if st.sidebar.button("🔕 Unsubscribe", use_container_width=True):
            st.session_state.telegram_subscribed = False
            st.sidebar.info("Unsubscribed from daily alerts.")
else:
    st.sidebar.markdown("""
    <div style='background:#f1f5f9;padding:12px;border-radius:10px;
    font-size:13px;color:#64748b;'>
        🔍 Search a city first to enable Telegram alerts.
    </div>
    """, unsafe_allow_html=True)

# =========================================
# CITY INPUT — always visible at top
# =========================================
st.markdown("<h1 style='text-align:center;'>🌫️ AQI MONITOR</h1>", unsafe_allow_html=True)

col_inp, col_btn = st.columns([4, 1])
with col_inp:
    city = st.text_input("Enter City", placeholder="Delhi, Mumbai, Chennai...", label_visibility="collapsed")
with col_btn:
    check = st.button("🔍 Check AQI", use_container_width=True)

# On button click → fetch and store in session_state
if check:
    if city.strip():
        with st.spinner(f"Fetching AQI for {city}..."):
            raw, missing = fetch(city)
            weather      = fetch_weather(city)
        if not raw:
            st.error("❌ City not found. Try a different spelling.")
            st.session_state.aqi_data = None
        else:
            available = [v for v in raw.values() if v is not None]
            aqi       = int(max(available))
            st.session_state.aqi_data = {
                "raw":     raw,
                "aqi":     aqi,
                "city":    city,
                "weather": weather,
            }
    else:
        st.warning("Please enter a city name.")

# =========================================
# RENDER — only if we have data
# =========================================
if st.session_state.aqi_data is None:
    st.info("👆 Enter a city above and click **Check AQI** to begin.")
    st.stop()

# Unpack stored data
raw     = st.session_state.aqi_data["raw"]
aqi     = st.session_state.aqi_data["aqi"]
city    = st.session_state.aqi_data["city"]
weather = st.session_state.aqi_data["weather"]

cat, text_color, bg = category(aqi)

# =========================================================
# PAGE: AQI MONITOR  (default view)
# =========================================================
if feature == "📊 AQI Monitor":

    # AQI CARD
    st.markdown(f"""
    <style>
    .dynamic-card{{
        background:{bg}; padding:50px; border-radius:25px;
        text-align:center; margin-top:10px; margin-bottom:20px;
    }}
    .aqi-number{{font-size:80px;font-weight:bold;color:{text_color};margin:10px 0;}}
    .aqi-cat   {{font-size:32px;font-weight:600;color:{text_color};}}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="dynamic-card">
        <h2>{city.upper()}</h2>
        <div class="aqi-number">{aqi}</div>
        <div class="aqi-cat">{cat}</div>
    </div>
    """, unsafe_allow_html=True)

    # LIVE WEATHER
    if weather:
        st.markdown("## ☁️ Live Weather")
        w1, w2, w3, w4 = st.columns(4)
        w1.metric("Temperature", f"{weather['temp']} °C")
        w2.metric("Humidity",    f"{weather['humidity']}%")
        w3.metric("Wind Speed",  f"{weather['wind']} m/s")
        w4.metric("Condition",   weather['condition'])
        if weather["wind"] < 2:
            st.warning("🌬️ Low wind speed — pollutants may be trapped near the surface.")
        if weather["humidity"] > 70:
            st.warning("💧 High humidity — may worsen respiratory symptoms.")

    # SOLUTIONS
    st.markdown("## 🛡️ Protective Measures")
    tips = solutions(aqi)
    c1, c2, c3, c4 = st.columns(4)
    for col, tip in zip([c1, c2, c3, c4], tips):
        col.markdown(f'<div class="solution">{tip}</div>', unsafe_allow_html=True)

    # HEALTH
    st.markdown("## ❤️ Health Challenges")
    risks = health(aqi)
    h1, h2, h3 = st.columns(3)
    h1.markdown(f'<div class="health"><b>🫁 Respiratory</b><br><br>{risks[0]}</div>', unsafe_allow_html=True)
    h2.markdown(f'<div class="health"><b>❤️ Heart</b><br><br>{risks[1]}</div>',       unsafe_allow_html=True)
    h3.markdown(f'<div class="health"><b>🤧 Allergy</b><br><br>{risks[2]}</div>',     unsafe_allow_html=True)

    # POLLUTANTS
    st.markdown("## 📊 Pollutants")
    df = pd.DataFrame(
        [(k, v) for k, v in raw.items() if v is not None],
        columns=["Pollutant", "Value"]
    )
    st.bar_chart(df.set_index("Pollutant"))

    st.caption("💡 Use the **sidebar** to explore Personalized Health Risk, 7-Day Forecast, and Activity Planner.")


# =========================================================
# PAGE: PERSONALIZED HEALTH RISK
# =========================================================
elif feature == "👤 Personalized Health Risk":

    st.markdown(f"""
    <div style="background:{bg};padding:20px 30px;border-radius:18px;
    margin-bottom:20px;text-align:center;">
        <span style="font-size:18px;color:{text_color};font-weight:600;">
            Current AQI in {city.upper()}: {aqi} — {cat}
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Enter Your Health Profile")
    st.caption("Your risk score is calculated from AQI + your personal health factors.")

    with st.form("health_form"):
        col_a, col_b, col_c = st.columns(3)
        age        = col_a.number_input("Your Age", min_value=1, max_value=110, value=30)
        has_asthma = col_b.checkbox("I have Asthma / Respiratory condition")
        has_heart  = col_c.checkbox("I have a Heart condition")
        submitted  = st.form_submit_button("🧮 Calculate My Risk", use_container_width=True)

    if submitted:
        score, label, color, bgcolor, advice_list, age_bonus, asthma_bonus, heart_bonus = \
            personal_risk_score(aqi, age, has_asthma, has_heart)

        # SCORE GAUGE
        st.markdown(f"""
        <div class="risk-box" style="background:{bgcolor};color:{color};border:2px solid {color};">
            {label} &nbsp;|&nbsp; Risk Score: {score} / 100
        </div>
        """, unsafe_allow_html=True)

        # PROGRESS BAR
        st.progress(score / 100)

        # DETAILED ADVICE
        st.markdown("#### 📋 Personalised Advice for You")
        for tip in advice_list:
            st.markdown(f"- {tip}")

        # SCORE BREAKDOWN
        with st.expander("🔍 See how your score was calculated", expanded=True):
            aqi_contrib = score - age_bonus - asthma_bonus - heart_bonus
            rows = [
                {"Factor": "AQI Level", "Points Added": aqi_contrib,
                 "Reason": f"AQI {aqi} → base risk"},
            ]
            if age < 12:
                rows.append({"Factor": "Age < 12", "Points Added": age_bonus,
                             "Reason": "Children have developing lungs"})
            elif age >= 65:
                rows.append({"Factor": "Age ≥ 65", "Points Added": age_bonus,
                             "Reason": "Elderly are more vulnerable"})
            elif age >= 50:
                rows.append({"Factor": "Age 50–64", "Points Added": age_bonus,
                             "Reason": "Moderately elevated vulnerability"})
            if has_asthma:
                rows.append({"Factor": "Asthma / Respiratory", "Points Added": asthma_bonus,
                             "Reason": "Pollutants trigger asthma"})
            if has_heart:
                rows.append({"Factor": "Heart Condition", "Points Added": heart_bonus,
                             "Reason": "Fine particles strain the heart"})
            rows.append({"Factor": "**TOTAL**", "Points Added": score, "Reason": "Capped at 100"})
            st.table(pd.DataFrame(rows))

        # COMPARISON WITH GENERAL POPULATION
        st.markdown("#### 👥 How Does Your Risk Compare?")
        comp_col1, comp_col2, comp_col3 = st.columns(3)
        general_score, *_ = personal_risk_score(aqi, 30, False, False)
        comp_col1.metric("General Public", f"{general_score}/100")
        comp_col2.metric("Your Score", f"{score}/100",
                         delta=f"+{score - general_score}" if score > general_score else f"{score - general_score}")
        comp_col3.metric("Max Possible", "100/100")


# =========================================================
# PAGE: 7-DAY AQI FORECAST
# =========================================================
elif feature == "📅 7-Day AQI Forecast":

    st.markdown(f"""
    <div style="background:{bg};padding:20px 30px;border-radius:18px;
    margin-bottom:20px;text-align:center;">
        <span style="font-size:18px;color:{text_color};font-weight:600;">
            Current AQI in {city.upper()}: {aqi} — {cat}
        </span>
    </div>
    """, unsafe_allow_html=True)

    forecast = generate_forecast(aqi, city)
    w_day    = worst_day(forecast)
    b_day    = best_day(forecast)

    # ALERT ROW
    alert_col1, alert_col2 = st.columns(2)
    w_cat, _, _ = category(int(w_day["aqi"]))
    b_cat, _, _ = category(int(b_day["aqi"]))
    alert_col1.error(
        f"⚠️ **Worst day:** {w_day['date'].replace(chr(10),' ')} "
        f"— AQI {w_day['aqi']} ({w_cat})"
    )
    alert_col2.success(
        f"✅ **Best day:** {b_day['date'].replace(chr(10),' ')} "
        f"— AQI {b_day['aqi']} ({b_cat})"
    )

    # 7 FORECAST CARDS
    st.markdown("### 📆 Day-by-Day Forecast")
    fcols = st.columns(7)
    for col, day in zip(fcols, forecast):
        day_aqi   = day["aqi"]
        day_color = forecast_color(day_aqi)
        d_cat, d_text, d_bg = category(int(day_aqi))
        col.markdown(f"""
        <div class="forecast-card" style="border-top:4px solid {day_color};">
            <div style="font-size:11px;color:#555;font-weight:600;white-space:pre-line;">
                {day['date']}
            </div>
            <div style="font-size:26px;font-weight:bold;color:{day_color};margin:8px 0;">
                {int(day_aqi)}
            </div>
            <div style="font-size:9px;color:{day_color};font-weight:700;letter-spacing:.5px;">
                {d_cat}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # LINE CHART
    st.markdown("### 📈 AQI Trend Chart")
    forecast_df = pd.DataFrame({
        "Date": [d["date"].replace("\n", " ") for d in forecast],
        "AQI":  [d["aqi"] for d in forecast]
    }).set_index("Date")
    st.line_chart(forecast_df, use_container_width=True)

    # TREND VERDICT
    first_aqi = forecast[0]["aqi"]
    last_aqi  = forecast[-1]["aqi"]
    st.markdown("### 🧭 Trend Direction")
    if last_aqi > first_aqi * 1.1:
        st.error("📈 AQI is trending **WORSE** over the next 7 days. Prepare precautions.")
    elif last_aqi < first_aqi * 0.9:
        st.success("📉 AQI is trending **BETTER** over the next 7 days. Conditions improving!")
    else:
        st.info("➡️ AQI is expected to remain **STABLE** over the next 7 days.")

    # SAFE DAY SUMMARY TABLE
    st.markdown("### 🗓️ Weekly Summary Table")
    summary = []
    for day in forecast:
        d_cat, _, _ = category(int(day["aqi"]))
        safe_icon = "✅" if day["aqi"] <= 100 else ("⚠️" if day["aqi"] <= 200 else "🚫")
        summary.append({
            "Day":          day["date"].replace("\n", " "),
            "Est. AQI":     int(day["aqi"]),
            "Category":     d_cat,
            "Safe Outdoor": safe_icon,
        })
    st.table(pd.DataFrame(summary))

    st.caption("ℹ️ Forecast is simulated based on current AQI with realistic daily variation.")


# =========================================================
# PAGE: OUTDOOR ACTIVITY PLANNER
# =========================================================
elif feature == "🏃 Outdoor Activity Planner":

    st.markdown(f"""
    <div style="background:{bg};padding:20px 30px;border-radius:18px;
    margin-bottom:20px;text-align:center;">
        <span style="font-size:18px;color:{text_color};font-weight:600;">
            Current AQI in {city.upper()}: {aqi} — {cat}
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ACTIVITY PICKER
    st.markdown("### 🎯 Select Your Activity")
    activity = st.selectbox(
        "What are you planning to do?",
        list(ACTIVITY_LIMITS.keys()),
        key="activity_select"
    )

    status, act_msg = activity_advice(aqi, activity)
    best_time       = best_time_message(aqi)

    # RESULT CARD
    st.markdown("### 🚦 Today's Recommendation")
    if status == "safe":
        st.markdown(f'<div class="activity-card" style="font-size:18px;">{act_msg}</div>',
                    unsafe_allow_html=True)
    elif status == "moderate":
        st.markdown(f'<div class="activity-warn" style="font-size:18px;">{act_msg}</div>',
                    unsafe_allow_html=True)
    else:
        st.error(act_msg)

    # BEST TIME BOX
    st.markdown(f"""
    <div class="forecast-card" style="margin-top:12px;padding:20px;">
        <div style="font-size:16px;font-weight:700;margin-bottom:8px;">⏰ Best Time to Go Outside Today</div>
        <div style="font-size:15px;color:#374151;">{best_time}</div>
    </div>
    """, unsafe_allow_html=True)

    # HOURLY AQI ESTIMATE
    st.markdown("### 🕐 Estimated Hourly AQI Today")
    st.caption("Rush hours (7–10 AM, 5–8 PM) tend to be worse due to traffic.")
    hourly = hourly_heatmap(aqi)
    hourly_df = pd.DataFrame(hourly)

    import plotly.graph_objects as go

    bar_colors = [forecast_color(v) for v in hourly_df["Est. AQI"]]
    fig = go.Figure(go.Bar(
        x=hourly_df["Hour"],
        y=hourly_df["Est. AQI"],
        marker_color=bar_colors,
        text=hourly_df["Est. AQI"],
        textposition="outside",
    ))
    fig.update_layout(
        xaxis_title="Hour of Day",
        yaxis_title="Est. AQI",
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=350,
        margin=dict(t=20, b=40),
        xaxis=dict(tickangle=-45),
    )
    st.plotly_chart(fig, use_container_width=True)

    # BEST HOURS TABLE
    best_hours = sorted(hourly, key=lambda x: x["Est. AQI"])[:5]
    st.markdown("#### 🏆 5 Best Hours Today")
    st.table(pd.DataFrame(best_hours))

    # ALL ACTIVITIES TABLE
    st.markdown("### 📋 All Activities — Today's AQI Safety")
    rows = []
    for act in ACTIVITY_LIMITS:
        s, msg = activity_advice(aqi, act)
        emoji  = "✅ Safe" if s == "safe" else ("⚠️ Moderate" if s == "moderate" else "🚫 Unsafe")
        rows.append({
            "Activity": act,
            "Status":   emoji,
            "Safe AQI Limit":  f"≤ {ACTIVITY_LIMITS[act]['safe']}",
            "Risky AQI Limit": f"≤ {ACTIVITY_LIMITS[act]['risky']}",
        })
    st.table(pd.DataFrame(rows))