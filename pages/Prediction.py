


# import streamlit as st
# import pandas as pd
# import numpy as np
# import requests
# import schedule
# import threading
# import time
# from datetime import datetime, timedelta
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # =========================================
# # PAGE CONFIG
# # =========================================
# st.set_page_config(
#     page_title="Prediction",
#     layout="wide"
# )

# # =========================================
# # SESSION STATE INIT
# # Keeps AQI data alive across all reruns
# # =========================================
# if "aqi_data" not in st.session_state:
#     st.session_state.aqi_data = None

# # =========================================
# # API KEYS
# # =========================================

# API = os.getenv("AQICN_API_KEY")
# OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")
# BOT_TOKEN = os.getenv("BOT_TOKEN")
# CHAT_ID = os.getenv("CHAT_ID")

# # =========================================
# # GLOBAL CSS
# # =========================================
# st.markdown("""
# <style>
# [data-testid="stSidebarNav"] ul li:first-child { display:none; }

# .stApp { background:white; }

# .solution{
#     background:white; padding:15px; border-radius:12px;
#     text-align:center; color:#111827; font-weight:600;
#     min-height:90px; display:flex; align-items:center;
#     justify-content:center; box-shadow:0 2px 8px rgba(0,0,0,.08);
# }

# .health{
#     background:linear-gradient(135deg,#1e293b,#0f172a);
#     padding:20px; border-radius:15px; text-align:center; color:white;
# }

# .metric-box{
#     background:#f5f7fb; padding:25px; border-radius:18px;
#     box-shadow:0 2px 8px rgba(0,0,0,.08); text-align:center;
#     margin-bottom:20px; border-left:6px solid #22c55e;
# }

# .metric-name  { font-size:20px; font-weight:600; color:#111827; }
# .metric-value { font-size:34px; font-weight:bold; margin-top:10px; color:#1e293b; }

# .risk-box{
#     padding:22px; border-radius:16px; text-align:center;
#     font-weight:700; font-size:22px; margin-bottom:10px;
# }

# .forecast-card{
#     background:#f5f7fb; padding:14px; border-radius:12px;
#     text-align:center; box-shadow:0 2px 6px rgba(0,0,0,.07);
# }

# .activity-card{
#     background:#f0fdf4; border-left:5px solid #22c55e;
#     padding:16px; border-radius:12px; margin-bottom:10px;
#     font-weight:600;
# }

# .activity-warn{
#     background:#fff7ed; border-left:5px solid #f97316;
#     padding:16px; border-radius:12px; margin-bottom:10px;
#     font-weight:600;
# }

# .section-header{
#     font-size:26px; font-weight:700; margin-bottom:6px; color:#1e293b;
# }

# .sidebar-feature-info{
#     background:#f1f5f9; padding:14px; border-radius:12px;
#     font-size:13px; color:#475569; margin-top:10px; line-height:1.6;
# }
# </style>
# """, unsafe_allow_html=True)


# # =========================================
# # FETCH AQI
# # =========================================
# def fetch(city):
#     url = f"https://api.waqi.info/feed/{city}/?token={API}"
#     res = requests.get(url).json()
#     if res["status"] != "ok":
#         return None, None
#     iaqi = res["data"]["iaqi"]
#     raw = {
#         "PM2.5": iaqi.get("pm25", {}).get("v"),
#         "PM10":  iaqi.get("pm10", {}).get("v"),
#         "NO2":   iaqi.get("no2",  {}).get("v"),
#         "SO2":   iaqi.get("so2",  {}).get("v"),
#         "CO":    iaqi.get("co",   {}).get("v"),
#         "O3":    iaqi.get("o3",   {}).get("v"),
#     }
#     vals = [v for v in raw.values() if v is not None]
#     if not vals:
#         return None, None
#     missing = sum(1 for v in raw.values() if v is None)
#     return raw, missing


# # =========================================
# # FETCH WEATHER
# # =========================================
# def fetch_weather(city):
#     url = (f"https://api.openweathermap.org/data/2.5/weather"
#            f"?q={city}&appid={OPENWEATHER_KEY}&units=metric")
#     try:
#         res = requests.get(url, timeout=10).json()
#         if str(res.get("cod")) != "200":
#             return None
#         return {
#             "temp":      res["main"]["temp"],
#             "humidity":  res["main"]["humidity"],
#             "wind":      res["wind"]["speed"],
#             "condition": res["weather"][0]["main"]
#         }
#     except:
#         return None


# # =========================================
# # TELEGRAM ALERT
# # =========================================
# def send_daily_alert():
#     city = "Delhi"
#     raw, _ = fetch(city)
#     if not raw:
#         return
#     aqi = int(max(v for v in raw.values() if v is not None))
#     advice = ("Air moderate. Outdoor okay." if aqi <= 100
#               else "Avoid jogging 8-10 AM." if aqi <= 200
#               else "Poor AQI. Stay cautious.")
#     msg = f"Daily AQI Forecast 🌫️\nCity: {city}\nAQI: {aqi}\n\nAdvice:\n{advice}"
#     requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
#                   data={"chat_id": CHAT_ID, "text": msg})


# # =========================================
# # AQI HELPERS
# # =========================================
# def category(aqi):
#     if aqi <= 50:    return "GOOD",         "#ffffff", "#00e600"
#     elif aqi <= 100: return "SATISFACTORY",  "#111827", "#9acd32"
#     elif aqi <= 200: return "MODERATE",      "#111827", "#fff000"
#     elif aqi <= 300: return "POOR",          "#ffffff", "#ff8800"
#     elif aqi <= 400: return "VERY POOR",     "#ffffff", "#ff1a1a"
#     else:            return "SEVERE",        "#ffffff", "#8b0029"

# def solutions(aqi):
#     if aqi <= 50:
#         return ["🌿 Outdoor activity safe","🏠 Ventilate home",
#                 "💧 Stay hydrated","🏃 Exercise recommended"]
#     elif aqi <= 100:
#         return ["😷 Mask if sensitive","🚶 Limit long exposure",
#                 "🪟 Keep windows closed","💧 Hydrate"]
#     elif aqi <= 200:
#         return ["😷 Wear N95","🏃 Avoid workouts outside",
#                 "🧴 Use purifier","🚗 Reduce traffic exposure"]
#     elif aqi <= 300:
#         return ["🏠 Stay indoors","🧴 Purifier continuously",
#                 "❌ Avoid exertion","😷 Mask outside"]
#     else:
#         return ["🚨 Strict indoor stay","😷 N95/N99 mask",
#                 "❌ Avoid exertion","👨‍👩‍👧 Protect elderly"]

# def health(aqi):
#     if aqi <= 50:
#         return ["No major respiratory issues","Very low heart stress","Minimal allergies"]
#     elif aqi <= 100:
#         return ["Mild irritation possible","Sensitive groups discomfort","Minor allergies possible"]
#     elif aqi <= 200:
#         return ["Breathing discomfort","Asthma symptoms possible","Fatigue possible"]
#     elif aqi <= 300:
#         return ["High asthma risk","Heart patients affected","Persistent coughing"]
#     else:
#         return ["Severe respiratory distress","Serious heart strain","Dangerous for all"]


# # =========================================
# # FEATURE 1 HELPERS — Personalized Risk
# # =========================================
# def personal_risk_score(aqi, age, has_asthma, has_heart):
#     base = 0
#     if aqi <= 50:    base = 5
#     elif aqi <= 100: base = 20
#     elif aqi <= 200: base = 40
#     elif aqi <= 300: base = 55
#     else:            base = 65

#     age_bonus = 0
#     if age < 12 or age >= 65: age_bonus = 15
#     elif age >= 50:            age_bonus = 8

#     asthma_bonus = 12 if has_asthma else 0
#     heart_bonus  = 10 if has_heart  else 0

#     score = min(100, base + age_bonus + asthma_bonus + heart_bonus)

#     if score <= 20:
#         label   = "🟢 Low Risk"
#         color   = "#16a34a"
#         bgcolor = "#dcfce7"
#         advice  = [
#             "✅ Air quality is safe for your profile.",
#             "🏃 You can do normal outdoor activities.",
#             "💧 Stay hydrated and enjoy fresh air.",
#         ]
#     elif score <= 45:
#         label   = "🟡 Moderate Risk"
#         color   = "#ca8a04"
#         bgcolor = "#fef9c3"
#         advice  = [
#             "⚠️ Limit prolonged outdoor exposure.",
#             "😷 Carry your inhaler if you have one.",
#             "🪟 Keep windows closed during peak hours.",
#         ]
#     elif score <= 70:
#         label   = "🟠 High Risk"
#         color   = "#ea580c"
#         bgcolor = "#fff7ed"
#         advice  = [
#             "🚫 Avoid all non-essential outdoor activity.",
#             "😷 Wear N95 mask if going outside.",
#             "🧴 Run air purifier indoors continuously.",
#             "💊 Keep medications accessible.",
#         ]
#     else:
#         label   = "🔴 Very High Risk"
#         color   = "#dc2626"
#         bgcolor = "#fef2f2"
#         advice  = [
#             "🚨 Stay strictly indoors.",
#             "😷 Wear N95/N99 even indoors if possible.",
#             "🏥 Seek medical advice if any breathing difficulty.",
#             "👨‍👩‍👧 Especially dangerous for your age/condition.",
#         ]

#     return score, label, color, bgcolor, advice, age_bonus, asthma_bonus, heart_bonus


# # =========================================
# # FEATURE 2 HELPERS — 7-Day Forecast
# # =========================================
# def generate_forecast(current_aqi, city):
#     np.random.seed(abs(hash(city)) % (2**31))
#     forecast = []
#     aqi = current_aqi
#     for i in range(7):
#         date  = (datetime.today() + timedelta(days=i)).strftime("%a\n%d %b")
#         drift = np.random.uniform(-0.15, 0.15) * aqi
#         aqi   = max(10, min(500, aqi + drift))
#         forecast.append({"date": date, "aqi": round(aqi, 1)})
#     return forecast

# def worst_day(forecast):
#     return max(forecast, key=lambda x: x["aqi"])

# def best_day(forecast):
#     return min(forecast, key=lambda x: x["aqi"])

# def forecast_color(aqi):
#     if aqi <= 50:    return "#00e600"
#     elif aqi <= 100: return "#9acd32"
#     elif aqi <= 200: return "#fbbf24"
#     elif aqi <= 300: return "#f97316"
#     elif aqi <= 400: return "#ef4444"
#     else:            return "#7f1d1d"


# # =========================================
# # FEATURE 3 HELPERS — Activity Planner
# # =========================================
# ACTIVITY_LIMITS = {
#     "🏃 Jogging / Running":   {"safe": 100, "risky": 200},
#     "🚴 Cycling":             {"safe": 100, "risky": 200},
#     "🧓 Elderly Walking":     {"safe":  50, "risky": 100},
#     "👦 Kids Outdoor Play":   {"safe":  50, "risky": 100},
#     "🧘 Yoga / Stretching":   {"safe": 150, "risky": 250},
#     "🏋️ Intense Gym Outdoor": {"safe":  75, "risky": 150},
# }

# def activity_advice(aqi, activity):
#     key    = activity
#     limits = ACTIVITY_LIMITS.get(key, {"safe": 100, "risky": 200})
#     name   = activity.split(" ", 1)[1] if " " in activity else activity
#     if aqi <= limits["safe"]:
#         return "safe",     f"✅ Safe to do **{name}** right now!"
#     elif aqi <= limits["risky"]:
#         return "moderate", f"⚠️ Moderate risk for **{name}**. Consider wearing a mask."
#     else:
#         return "unsafe",   f"🚫 **{name}** is not recommended outdoors today."

# def best_time_message(aqi):
#     if aqi <= 100:   return "🕕 Any time is fine. Morning (6–8 AM) is typically freshest."
#     elif aqi <= 200: return "🕔 Prefer early morning (5–7 AM) before traffic peaks."
#     else:            return "🚫 No outdoor time recommended today. Stay indoors."

# def hourly_heatmap(aqi):
#     """Returns list of (hour_label, relative_aqi) for 24 hours."""
#     hours = []
#     for h in range(24):
#         # Traffic rush hours are worse
#         if 7 <= h <= 10 or 17 <= h <= 20:
#             factor = 1.3
#         elif 1 <= h <= 5:
#             factor = 0.75
#         else:
#             factor = 1.0
#         hours.append({
#             "Hour": f"{h:02d}:00",
#             "Est. AQI": round(aqi * factor)
#         })
#     return hours


# # =========================================
# # SIDEBAR — Navigation
# # =========================================
# st.sidebar.markdown("""
# <style>
# .aqi-box{
#     background:#f3f4f6; padding:20px; border-radius:18px;
#     box-shadow:0 2px 8px rgba(0,0,0,.08);
# }
# .aqi-title{ font-size:22px; font-weight:bold; margin-bottom:14px; }
# .aqi-tag{
#     padding:10px 14px; border-radius:8px; font-weight:600;
#     margin-bottom:6px; color:white;
# }
# .good         { background:#00e600; }
# .satisfactory { background:#9acd32; color:black !important; }
# .moderate     { background:#fff000; color:black !important; }
# .poor         { background:#ff8800; }
# .verypoor     { background:#ff1a1a; }
# .severe       { background:#8b0029; }
# </style>

# <div class="aqi-box">
# <div class="aqi-title">🎨 AQI Scale</div>
# <div class="aqi-tag good">🙂 Good (0–50)</div>
# <div class="aqi-tag satisfactory">🙂 Satisfactory (51–100)</div>
# <div class="aqi-tag moderate">😐 Moderate (101–200)</div>
# <div class="aqi-tag poor">😷 Poor (201–300)</div>
# <div class="aqi-tag verypoor">🤢 Very Poor (301–400)</div>
# <div class="aqi-tag severe">☠️ Severe (401+)</div>
# </div>
# """, unsafe_allow_html=True)

# st.sidebar.markdown("---")
# st.sidebar.markdown("### 🔧 Features")

# # Radio acts as sidebar navigation for the 3 features
# feature = st.sidebar.radio(
#     "Select a feature to explore:",
#     options=[
#         "📊 AQI Monitor",
#         "👤 Personalized Health Risk",
#         "📅 7-Day AQI Forecast",
#         "🏃 Outdoor Activity Planner",
#     ],
#     key="sidebar_feature"
# )

# # Feature descriptions shown in sidebar
# descriptions = {
#     "📊 AQI Monitor": "Enter a city to get live AQI, pollutant breakdown, health advice, and weather.",
#     "👤 Personalized Health Risk": "Enter your age & health conditions to get a custom 0–100 risk score with detailed advice.",
#     "📅 7-Day AQI Forecast": "See a simulated 7-day AQI trend with worst/best day alerts and improving/worsening direction.",
#     "🏃 Outdoor Activity Planner": "Pick your activity (jogging, cycling, etc.) to see if today's AQI is safe + best time to go.",
# }
# st.sidebar.markdown(
#     f'<div class="sidebar-feature-info">ℹ️ {descriptions[feature]}</div>',
#     unsafe_allow_html=True
# )

# # =========================================
# # SIDEBAR — TELEGRAM ALERT BUTTON
# # =========================================
# st.sidebar.markdown("---")
# st.sidebar.markdown("### 📲 Telegram Alerts")
# st.sidebar.caption("Get instant AQI alert + daily updates at 8 AM on Telegram.")

# # Session flag so we only show the button once per session
# if "telegram_subscribed" not in st.session_state:
#     st.session_state.telegram_subscribed = False

# def build_telegram_message(city_name, aqi_val, raw_data, weather_data):
#     """Builds a rich Telegram message with current AQI data."""
#     import pytz
#     from datetime import datetime
#     IST      = pytz.timezone("Asia/Kolkata")
#     now_ist  = datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST")

#     # Category
#     if aqi_val <= 50:    cat_label, cat_emoji = "Good ✅",          "🟢"
#     elif aqi_val <= 100: cat_label, cat_emoji = "Satisfactory 🙂",  "🟡"
#     elif aqi_val <= 200: cat_label, cat_emoji = "Moderate 😐",       "🟠"
#     elif aqi_val <= 300: cat_label, cat_emoji = "Poor 😷",           "🔴"
#     elif aqi_val <= 400: cat_label, cat_emoji = "Very Poor 🤢",      "🔴"
#     else:                cat_label, cat_emoji = "Severe ☠️",         "⚫"

#     # Advice
#     if aqi_val <= 50:
#         advice = ["✅ Air is clean. Enjoy outdoor activities.", "💧 Stay hydrated."]
#     elif aqi_val <= 100:
#         advice = ["😷 Sensitive groups wear a mask.", "🚶 Limit long outdoor stays."]
#     elif aqi_val <= 200:
#         advice = ["😷 Wear N95 mask outdoors.", "🏃 Avoid jogging 8–10 AM.", "🧴 Use air purifier."]
#     elif aqi_val <= 300:
#         advice = ["🏠 Stay indoors.", "😷 N95/N99 mask if going out.", "❌ Avoid outdoor exercise."]
#     else:
#         advice = ["🚨 Stay strictly indoors.", "😷 N99 mask even indoors.", "🏥 Seek help if breathing issues."]

#     # Best time
#     if aqi_val <= 100:   outdoor_time = "🕕 Any time is fine. Morning (6–8 AM) is freshest."
#     elif aqi_val <= 200: outdoor_time = "🕔 Early morning (5–7 AM) before traffic peaks."
#     else:                outdoor_time = "🚫 Not recommended to go outside today."

#     # Pollutants
#     pollutant_lines = ""
#     if raw_data:
#         for k, v in raw_data.items():
#             if v is not None:
#                 pollutant_lines += f"  • {k}: {v}\n"

#     # Weather
#     weather_lines = ""
#     if weather_data:
#         weather_lines = (
#             f"\n☁️ *Weather in {city_name}*\n"
#             f"  🌡 Temp: {weather_data['temp']}°C\n"
#             f"  💧 Humidity: {weather_data['humidity']}%\n"
#             f"  🌬 Wind: {weather_data['wind']} m/s\n"
#             f"  ⛅ Condition: {weather_data['condition']}\n"
#         )

#     msg = f"""🌫️ *AQI Alert — {city_name.upper()}*
# 📅 {now_ist}
# {'─' * 28}

# {cat_emoji} *AQI: {aqi_val}* — {cat_label}

# 💡 *Advice:*
# """ + "\n".join(f"  {t}" for t in advice) + f"""

# ⏰ *Best Outdoor Time:*
#   {outdoor_time}

# 🔬 *Pollutants:*
# {pollutant_lines}{weather_lines}
# {'─' * 28}
# 🔔 _You will now receive this alert daily at 8:00 AM IST._
# _Powered by AQI Monitor App_"""

#     return msg


# def send_telegram_alert(city_name, aqi_val, raw_data, weather_data):
#     """Sends the alert message via Telegram Bot API."""
#     msg = build_telegram_message(city_name, aqi_val, raw_data, weather_data)
#     url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
#     try:
#         res = requests.post(url, data={
#             "chat_id":    CHAT_ID,
#             "text":       msg,
#             "parse_mode": "Markdown",
#         }, timeout=15)
#         return res.status_code == 200, res.text
#     except Exception as e:
#         return False, str(e)


# # Show button only if AQI data is available
# if st.session_state.aqi_data is not None:
#     if not st.session_state.telegram_subscribed:
#         if st.sidebar.button(
#             "📩 Send Alert & Subscribe to Daily Updates",
#             use_container_width=True,
#             type="primary"
#         ):
#             with st.sidebar:
#                 with st.spinner("Sending alert to Telegram..."):
#                     ok, err = send_telegram_alert(
#                         st.session_state.aqi_data["city"],
#                         st.session_state.aqi_data["aqi"],
#                         st.session_state.aqi_data["raw"],
#                         st.session_state.aqi_data["weather"],
#                     )
#             if ok:
#                 st.session_state.telegram_subscribed = True
#                 st.sidebar.success("✅ Alert sent! Opening Telegram...")
#                 # Auto-open Telegram after 1 second
#                 st.sidebar.markdown(
#                     """
#                     <script>
#                     setTimeout(function(){
#                         window.open('https://t.me/aqi_alert_2026_bot', '_blank');
#                     }, 800);
#                     </script>
#                     """,
#                     unsafe_allow_html=True
#                 )
#                 # Fallback clickable link
#                 st.sidebar.markdown(
#                     "👉 [Open Telegram Bot](https://t.me/aqi_alert_2026_bot)",
#                     unsafe_allow_html=True
#                 )
#             else:
#                 st.sidebar.error(f"❌ Failed to send. Check bot token.\n{err}")
#     else:
#         # Already subscribed — show status
#         st.sidebar.markdown("""
#         <div style='background:#dcfce7;padding:12px;border-radius:10px;
#         border-left:4px solid #16a34a;font-size:13px;color:#166534;'>
#             ✅ <b>Subscribed!</b><br>
#             You'll receive daily AQI alerts at<br>
#             <b>8:00 AM IST</b> on Telegram.
#         </div>
#         """, unsafe_allow_html=True)
#         st.sidebar.markdown(
#             "👉 [Open Telegram Bot](https://t.me/aqi_alert_2026_bot)",
#             unsafe_allow_html=True
#         )
#         # Allow unsubscribe
#         if st.sidebar.button("🔕 Unsubscribe", use_container_width=True):
#             st.session_state.telegram_subscribed = False
#             st.sidebar.info("Unsubscribed from daily alerts.")
# else:
#     st.sidebar.markdown("""
#     <div style='background:#f1f5f9;padding:12px;border-radius:10px;
#     font-size:13px;color:#64748b;'>
#         🔍 Search a city first to enable Telegram alerts.
#     </div>
#     """, unsafe_allow_html=True)

# # =========================================
# # CITY INPUT — always visible at top
# # =========================================
# st.markdown("<h1 style='text-align:center;'>🌫️ AQI MONITOR</h1>", unsafe_allow_html=True)

# col_inp, col_btn = st.columns([4, 1])
# with col_inp:
#     city = st.text_input("Enter City", placeholder="Delhi, Mumbai, Chennai...", label_visibility="collapsed")
# with col_btn:
#     check = st.button("🔍 Check AQI", use_container_width=True)

# # On button click → fetch and store in session_state
# if check:
#     if city.strip():
#         with st.spinner(f"Fetching AQI for {city}..."):
#             raw, missing = fetch(city)
#             weather      = fetch_weather(city)
#         if not raw:
#             st.error("❌ City not found. Try a different spelling.")
#             st.session_state.aqi_data = None
#         else:
#             available = [v for v in raw.values() if v is not None]
#             aqi       = int(max(available))
#             st.session_state.aqi_data = {
#                 "raw":     raw,
#                 "aqi":     aqi,
#                 "city":    city,
#                 "weather": weather,
#             }
#     else:
#         st.warning("Please enter a city name.")

# # =========================================
# # RENDER — only if we have data
# # =========================================
# if st.session_state.aqi_data is None:
#     st.info("👆 Enter a city above and click **Check AQI** to begin.")
#     st.stop()

# # Unpack stored data
# raw     = st.session_state.aqi_data["raw"]
# aqi     = st.session_state.aqi_data["aqi"]
# city    = st.session_state.aqi_data["city"]
# weather = st.session_state.aqi_data["weather"]

# cat, text_color, bg = category(aqi)

# # =========================================================
# # PAGE: AQI MONITOR  (default view)
# # =========================================================
# if feature == "📊 AQI Monitor":

#     # AQI CARD
#     st.markdown(f"""
#     <style>
#     .dynamic-card{{
#         background:{bg}; padding:50px; border-radius:25px;
#         text-align:center; margin-top:10px; margin-bottom:20px;
#     }}
#     .aqi-number{{font-size:80px;font-weight:bold;color:{text_color};margin:10px 0;}}
#     .aqi-cat   {{font-size:32px;font-weight:600;color:{text_color};}}
#     </style>
#     """, unsafe_allow_html=True)

#     st.markdown(f"""
#     <div class="dynamic-card">
#         <h2>{city.upper()}</h2>
#         <div class="aqi-number">{aqi}</div>
#         <div class="aqi-cat">{cat}</div>
#     </div>
#     """, unsafe_allow_html=True)

#     # LIVE WEATHER
#     if weather:
#         st.markdown("## ☁️ Live Weather")
#         w1, w2, w3, w4 = st.columns(4)
#         w1.metric("Temperature", f"{weather['temp']} °C")
#         w2.metric("Humidity",    f"{weather['humidity']}%")
#         w3.metric("Wind Speed",  f"{weather['wind']} m/s")
#         w4.metric("Condition",   weather['condition'])
#         if weather["wind"] < 2:
#             st.warning("🌬️ Low wind speed — pollutants may be trapped near the surface.")
#         if weather["humidity"] > 70:
#             st.warning("💧 High humidity — may worsen respiratory symptoms.")

#     # SOLUTIONS
#     st.markdown("## 🛡️ Protective Measures")
#     tips = solutions(aqi)
#     c1, c2, c3, c4 = st.columns(4)
#     for col, tip in zip([c1, c2, c3, c4], tips):
#         col.markdown(f'<div class="solution">{tip}</div>', unsafe_allow_html=True)

#     # HEALTH
#     st.markdown("## ❤️ Health Challenges")
#     risks = health(aqi)
#     h1, h2, h3 = st.columns(3)
#     h1.markdown(f'<div class="health"><b>🫁 Respiratory</b><br><br>{risks[0]}</div>', unsafe_allow_html=True)
#     h2.markdown(f'<div class="health"><b>❤️ Heart</b><br><br>{risks[1]}</div>',       unsafe_allow_html=True)
#     h3.markdown(f'<div class="health"><b>🤧 Allergy</b><br><br>{risks[2]}</div>',     unsafe_allow_html=True)

#     # POLLUTANTS
#     st.markdown("## 📊 Pollutants")
#     df = pd.DataFrame(
#         [(k, v) for k, v in raw.items() if v is not None],
#         columns=["Pollutant", "Value"]
#     )
#     st.bar_chart(df.set_index("Pollutant"))

#     st.caption("💡 Use the **sidebar** to explore Personalized Health Risk, 7-Day Forecast, and Activity Planner.")


# # =========================================================
# # PAGE: PERSONALIZED HEALTH RISK
# # =========================================================
# elif feature == "👤 Personalized Health Risk":

#     st.markdown(f"""
#     <div style="background:{bg};padding:20px 30px;border-radius:18px;
#     margin-bottom:20px;text-align:center;">
#         <span style="font-size:18px;color:{text_color};font-weight:600;">
#             Current AQI in {city.upper()}: {aqi} — {cat}
#         </span>
#     </div>
#     """, unsafe_allow_html=True)

#     st.markdown("### Enter Your Health Profile")
#     st.caption("Your risk score is calculated from AQI + your personal health factors.")

#     with st.form("health_form"):
#         col_a, col_b, col_c = st.columns(3)
#         age        = col_a.number_input("Your Age", min_value=1, max_value=110, value=30)
#         has_asthma = col_b.checkbox("I have Asthma / Respiratory condition")
#         has_heart  = col_c.checkbox("I have a Heart condition")
#         submitted  = st.form_submit_button("🧮 Calculate My Risk", use_container_width=True)

#     if submitted:
#         score, label, color, bgcolor, advice_list, age_bonus, asthma_bonus, heart_bonus = \
#             personal_risk_score(aqi, age, has_asthma, has_heart)

#         # SCORE GAUGE
#         st.markdown(f"""
#         <div class="risk-box" style="background:{bgcolor};color:{color};border:2px solid {color};">
#             {label} &nbsp;|&nbsp; Risk Score: {score} / 100
#         </div>
#         """, unsafe_allow_html=True)

#         # PROGRESS BAR
#         st.progress(score / 100)

#         # DETAILED ADVICE
#         st.markdown("#### 📋 Personalised Advice for You")
#         for tip in advice_list:
#             st.markdown(f"- {tip}")

#         # SCORE BREAKDOWN
#         with st.expander("🔍 See how your score was calculated", expanded=True):
#             aqi_contrib = score - age_bonus - asthma_bonus - heart_bonus
#             rows = [
#                 {"Factor": "AQI Level", "Points Added": aqi_contrib,
#                  "Reason": f"AQI {aqi} → base risk"},
#             ]
#             if age < 12:
#                 rows.append({"Factor": "Age < 12", "Points Added": age_bonus,
#                              "Reason": "Children have developing lungs"})
#             elif age >= 65:
#                 rows.append({"Factor": "Age ≥ 65", "Points Added": age_bonus,
#                              "Reason": "Elderly are more vulnerable"})
#             elif age >= 50:
#                 rows.append({"Factor": "Age 50–64", "Points Added": age_bonus,
#                              "Reason": "Moderately elevated vulnerability"})
#             if has_asthma:
#                 rows.append({"Factor": "Asthma / Respiratory", "Points Added": asthma_bonus,
#                              "Reason": "Pollutants trigger asthma"})
#             if has_heart:
#                 rows.append({"Factor": "Heart Condition", "Points Added": heart_bonus,
#                              "Reason": "Fine particles strain the heart"})
#             rows.append({"Factor": "**TOTAL**", "Points Added": score, "Reason": "Capped at 100"})
#             st.table(pd.DataFrame(rows))

#         # COMPARISON WITH GENERAL POPULATION
#         st.markdown("#### 👥 How Does Your Risk Compare?")
#         comp_col1, comp_col2, comp_col3 = st.columns(3)
#         general_score, *_ = personal_risk_score(aqi, 30, False, False)
#         comp_col1.metric("General Public", f"{general_score}/100")
#         comp_col2.metric("Your Score", f"{score}/100",
#                          delta=f"+{score - general_score}" if score > general_score else f"{score - general_score}")
#         comp_col3.metric("Max Possible", "100/100")


# # =========================================================
# # PAGE: 7-DAY AQI FORECAST
# # =========================================================
# elif feature == "📅 7-Day AQI Forecast":

#     st.markdown(f"""
#     <div style="background:{bg};padding:20px 30px;border-radius:18px;
#     margin-bottom:20px;text-align:center;">
#         <span style="font-size:18px;color:{text_color};font-weight:600;">
#             Current AQI in {city.upper()}: {aqi} — {cat}
#         </span>
#     </div>
#     """, unsafe_allow_html=True)

#     forecast = generate_forecast(aqi, city)
#     w_day    = worst_day(forecast)
#     b_day    = best_day(forecast)

#     # ALERT ROW
#     alert_col1, alert_col2 = st.columns(2)
#     w_cat, _, _ = category(int(w_day["aqi"]))
#     b_cat, _, _ = category(int(b_day["aqi"]))
#     alert_col1.error(
#         f"⚠️ **Worst day:** {w_day['date'].replace(chr(10),' ')} "
#         f"— AQI {w_day['aqi']} ({w_cat})"
#     )
#     alert_col2.success(
#         f"✅ **Best day:** {b_day['date'].replace(chr(10),' ')} "
#         f"— AQI {b_day['aqi']} ({b_cat})"
#     )

#     # 7 FORECAST CARDS
#     st.markdown("### 📆 Day-by-Day Forecast")
#     fcols = st.columns(7)
#     for col, day in zip(fcols, forecast):
#         day_aqi   = day["aqi"]
#         day_color = forecast_color(day_aqi)
#         d_cat, d_text, d_bg = category(int(day_aqi))
#         col.markdown(f"""
#         <div class="forecast-card" style="border-top:4px solid {day_color};">
#             <div style="font-size:11px;color:#555;font-weight:600;white-space:pre-line;">
#                 {day['date']}
#             </div>
#             <div style="font-size:26px;font-weight:bold;color:{day_color};margin:8px 0;">
#                 {int(day_aqi)}
#             </div>
#             <div style="font-size:9px;color:{day_color};font-weight:700;letter-spacing:.5px;">
#                 {d_cat}
#             </div>
#         </div>
#         """, unsafe_allow_html=True)

#     # LINE CHART
#     st.markdown("### 📈 AQI Trend Chart")
#     forecast_df = pd.DataFrame({
#         "Date": [d["date"].replace("\n", " ") for d in forecast],
#         "AQI":  [d["aqi"] for d in forecast]
#     }).set_index("Date")
#     st.line_chart(forecast_df, use_container_width=True)

#     # TREND VERDICT
#     first_aqi = forecast[0]["aqi"]
#     last_aqi  = forecast[-1]["aqi"]
#     st.markdown("### 🧭 Trend Direction")
#     if last_aqi > first_aqi * 1.1:
#         st.error("📈 AQI is trending **WORSE** over the next 7 days. Prepare precautions.")
#     elif last_aqi < first_aqi * 0.9:
#         st.success("📉 AQI is trending **BETTER** over the next 7 days. Conditions improving!")
#     else:
#         st.info("➡️ AQI is expected to remain **STABLE** over the next 7 days.")

#     # SAFE DAY SUMMARY TABLE
#     st.markdown("### 🗓️ Weekly Summary Table")
#     summary = []
#     for day in forecast:
#         d_cat, _, _ = category(int(day["aqi"]))
#         safe_icon = "✅" if day["aqi"] <= 100 else ("⚠️" if day["aqi"] <= 200 else "🚫")
#         summary.append({
#             "Day":          day["date"].replace("\n", " "),
#             "Est. AQI":     int(day["aqi"]),
#             "Category":     d_cat,
#             "Safe Outdoor": safe_icon,
#         })
#     st.table(pd.DataFrame(summary))

#     st.caption("ℹ️ Forecast is simulated based on current AQI with realistic daily variation.")


# # =========================================================
# # PAGE: OUTDOOR ACTIVITY PLANNER
# # =========================================================
# elif feature == "🏃 Outdoor Activity Planner":

#     st.markdown(f"""
#     <div style="background:{bg};padding:20px 30px;border-radius:18px;
#     margin-bottom:20px;text-align:center;">
#         <span style="font-size:18px;color:{text_color};font-weight:600;">
#             Current AQI in {city.upper()}: {aqi} — {cat}
#         </span>
#     </div>
#     """, unsafe_allow_html=True)

#     # ACTIVITY PICKER
#     st.markdown("### 🎯 Select Your Activity")
#     activity = st.selectbox(
#         "What are you planning to do?",
#         list(ACTIVITY_LIMITS.keys()),
#         key="activity_select"
#     )

#     status, act_msg = activity_advice(aqi, activity)
#     best_time       = best_time_message(aqi)

#     # RESULT CARD
#     st.markdown("### 🚦 Today's Recommendation")
#     if status == "safe":
#         st.markdown(f'<div class="activity-card" style="font-size:18px;">{act_msg}</div>',
#                     unsafe_allow_html=True)
#     elif status == "moderate":
#         st.markdown(f'<div class="activity-warn" style="font-size:18px;">{act_msg}</div>',
#                     unsafe_allow_html=True)
#     else:
#         st.error(act_msg)

#     # BEST TIME BOX
#     st.markdown(f"""
#     <div class="forecast-card" style="margin-top:12px;padding:20px;">
#         <div style="font-size:16px;font-weight:700;margin-bottom:8px;">⏰ Best Time to Go Outside Today</div>
#         <div style="font-size:15px;color:#374151;">{best_time}</div>
#     </div>
#     """, unsafe_allow_html=True)

#     # HOURLY AQI ESTIMATE
#     st.markdown("### 🕐 Estimated Hourly AQI Today")
#     st.caption("Rush hours (7–10 AM, 5–8 PM) tend to be worse due to traffic.")
#     hourly = hourly_heatmap(aqi)
#     hourly_df = pd.DataFrame(hourly)

#     import plotly.graph_objects as go

#     bar_colors = [forecast_color(v) for v in hourly_df["Est. AQI"]]
#     fig = go.Figure(go.Bar(
#         x=hourly_df["Hour"],
#         y=hourly_df["Est. AQI"],
#         marker_color=bar_colors,
#         text=hourly_df["Est. AQI"],
#         textposition="outside",
#     ))
#     fig.update_layout(
#         xaxis_title="Hour of Day",
#         yaxis_title="Est. AQI",
#         plot_bgcolor="white",
#         paper_bgcolor="white",
#         height=350,
#         margin=dict(t=20, b=40),
#         xaxis=dict(tickangle=-45),
#     )
#     st.plotly_chart(fig, use_container_width=True)

#     # BEST HOURS TABLE
#     best_hours = sorted(hourly, key=lambda x: x["Est. AQI"])[:5]
#     st.markdown("#### 🏆 5 Best Hours Today")
#     st.table(pd.DataFrame(best_hours))

#     # ALL ACTIVITIES TABLE
#     st.markdown("### 📋 All Activities — Today's AQI Safety")
#     rows = []
#     for act in ACTIVITY_LIMITS:
#         s, msg = activity_advice(aqi, act)
#         emoji  = "✅ Safe" if s == "safe" else ("⚠️ Moderate" if s == "moderate" else "🚫 Unsafe")
#         rows.append({
#             "Activity": act,
#             "Status":   emoji,
#             "Safe AQI Limit":  f"≤ {ACTIVITY_LIMITS[act]['safe']}",
#             "Risky AQI Limit": f"≤ {ACTIVITY_LIMITS[act]['risky']}",
#         })
#     st.table(pd.DataFrame(rows))


################################################################################################################


# import streamlit as st
# import pandas as pd
# import numpy as np
# import requests
# import schedule
# import threading
# import time
# from datetime import datetime, timedelta
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # =========================================
# # PAGE CONFIG
# # =========================================
# st.set_page_config(
#     page_title="Prediction",
#     layout="wide"
# )

# # =========================================
# # SESSION STATE INIT
# # Keeps AQI data alive across all reruns
# # =========================================
# if "aqi_data" not in st.session_state:
#     st.session_state.aqi_data = None

# # =========================================
# # API KEYS
# # =========================================

# API = os.getenv("AQICN_API_KEY")
# OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")
# BOT_TOKEN = os.getenv("BOT_TOKEN")
# CHAT_ID = os.getenv("CHAT_ID")

# # =========================================
# # GLOBAL CSS
# # =========================================
# st.markdown("""
# <style>
# [data-testid="stSidebarNav"] ul li:first-child { display:none; }

# .stApp { background:white; }

# .solution{
#     background:white; padding:15px; border-radius:12px;
#     text-align:center; color:#111827; font-weight:600;
#     min-height:90px; display:flex; align-items:center;
#     justify-content:center; box-shadow:0 2px 8px rgba(0,0,0,.08);
# }

# .health{
#     background:linear-gradient(135deg,#1e293b,#0f172a);
#     padding:20px; border-radius:15px; text-align:center; color:white;
# }

# .metric-box{
#     background:#f5f7fb; padding:25px; border-radius:18px;
#     box-shadow:0 2px 8px rgba(0,0,0,.08); text-align:center;
#     margin-bottom:20px; border-left:6px solid #22c55e;
# }

# .metric-name  { font-size:20px; font-weight:600; color:#111827; }
# .metric-value { font-size:34px; font-weight:bold; margin-top:10px; color:#1e293b; }

# .risk-box{
#     padding:22px; border-radius:16px; text-align:center;
#     font-weight:700; font-size:22px; margin-bottom:10px;
# }

# .forecast-card{
#     background:#f5f7fb; padding:14px; border-radius:12px;
#     text-align:center; box-shadow:0 2px 6px rgba(0,0,0,.07);
# }

# .activity-card{
#     background:#f0fdf4; border-left:5px solid #22c55e;
#     padding:16px; border-radius:12px; margin-bottom:10px;
#     font-weight:600;
# }

# .activity-warn{
#     background:#fff7ed; border-left:5px solid #f97316;
#     padding:16px; border-radius:12px; margin-bottom:10px;
#     font-weight:600;
# }

# .section-header{
#     font-size:26px; font-weight:700; margin-bottom:6px; color:#1e293b;
# }

# .sidebar-feature-info{
#     background:#f1f5f9; padding:14px; border-radius:12px;
#     font-size:13px; color:#475569; margin-top:10px; line-height:1.6;
# }
# </style>
# """, unsafe_allow_html=True)


# # =========================================
# # FETCH AQI
# # =========================================
# def fetch(city):
#     url = f"https://api.waqi.info/feed/{city}/?token={API}"
#     res = requests.get(url).json()
#     if res["status"] != "ok":
#         return None, None
#     iaqi = res["data"]["iaqi"]
#     raw = {
#         "PM2.5": iaqi.get("pm25", {}).get("v"),
#         "PM10":  iaqi.get("pm10", {}).get("v"),
#         "NO2":   iaqi.get("no2",  {}).get("v"),
#         "SO2":   iaqi.get("so2",  {}).get("v"),
#         "CO":    iaqi.get("co",   {}).get("v"),
#         "O3":    iaqi.get("o3",   {}).get("v"),
#     }
#     vals = [v for v in raw.values() if v is not None]
#     if not vals:
#         return None, None
#     missing = sum(1 for v in raw.values() if v is None)
#     return raw, missing


# # =========================================
# # FETCH WEATHER
# # =========================================
# def fetch_weather(city):
#     url = (f"https://api.openweathermap.org/data/2.5/weather"
#            f"?q={city}&appid={OPENWEATHER_KEY}&units=metric")
#     try:
#         res = requests.get(url, timeout=10).json()
#         if str(res.get("cod")) != "200":
#             return None
#         return {
#             "temp":      res["main"]["temp"],
#             "humidity":  res["main"]["humidity"],
#             "wind":      res["wind"]["speed"],
#             "condition": res["weather"][0]["main"]
#         }
#     except:
#         return None


# # =========================================
# # TELEGRAM ALERT
# # =========================================
# def send_daily_alert():
#     city = "Delhi"
#     raw, _ = fetch(city)
#     if not raw:
#         return
#     aqi = int(max(v for v in raw.values() if v is not None))
#     advice = ("Air moderate. Outdoor okay." if aqi <= 100
#               else "Avoid jogging 8-10 AM." if aqi <= 200
#               else "Poor AQI. Stay cautious.")
#     msg = f"Daily AQI Forecast 🌫️\nCity: {city}\nAQI: {aqi}\n\nAdvice:\n{advice}"
#     requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
#                   data={"chat_id": CHAT_ID, "text": msg})


# # =========================================
# # AQI HELPERS
# # =========================================
# def category(aqi):
#     if aqi <= 50:    return "GOOD",         "#ffffff", "#00e600"
#     elif aqi <= 100: return "SATISFACTORY",  "#111827", "#9acd32"
#     elif aqi <= 200: return "MODERATE",      "#111827", "#fff000"
#     elif aqi <= 300: return "POOR",          "#ffffff", "#ff8800"
#     elif aqi <= 400: return "VERY POOR",     "#ffffff", "#ff1a1a"
#     else:            return "SEVERE",        "#ffffff", "#8b0029"

# def solutions(aqi):
#     if aqi <= 50:
#         return ["🌿 Outdoor activity safe","🏠 Ventilate home",
#                 "💧 Stay hydrated","🏃 Exercise recommended"]
#     elif aqi <= 100:
#         return ["😷 Mask if sensitive","🚶 Limit long exposure",
#                 "🪟 Keep windows closed","💧 Hydrate"]
#     elif aqi <= 200:
#         return ["😷 Wear N95","🏃 Avoid workouts outside",
#                 "🧴 Use purifier","🚗 Reduce traffic exposure"]
#     elif aqi <= 300:
#         return ["🏠 Stay indoors","🧴 Purifier continuously",
#                 "❌ Avoid exertion","😷 Mask outside"]
#     else:
#         return ["🚨 Strict indoor stay","😷 N95/N99 mask",
#                 "❌ Avoid exertion","👨‍👩‍👧 Protect elderly"]

# def health(aqi):
#     if aqi <= 50:
#         return ["No major respiratory issues","Very low heart stress","Minimal allergies"]
#     elif aqi <= 100:
#         return ["Mild irritation possible","Sensitive groups discomfort","Minor allergies possible"]
#     elif aqi <= 200:
#         return ["Breathing discomfort","Asthma symptoms possible","Fatigue possible"]
#     elif aqi <= 300:
#         return ["High asthma risk","Heart patients affected","Persistent coughing"]
#     else:
#         return ["Severe respiratory distress","Serious heart strain","Dangerous for all"]


# # =========================================
# # FEATURE 1 HELPERS — Personalized Risk
# # =========================================
# def personal_risk_score(aqi, age, has_asthma, has_heart):
#     # AQI base: linear interpolation within each band for smooth progression
#     if aqi <= 50:
#         base = 5 + (aqi / 50) * 10           # 5–15
#     elif aqi <= 100:
#         base = 15 + ((aqi - 50) / 50) * 15   # 15–30
#     elif aqi <= 200:
#         base = 30 + ((aqi - 100) / 100) * 20 # 30–50
#     elif aqi <= 300:
#         base = 50 + ((aqi - 200) / 100) * 15 # 50–65
#     else:
#         base = 65 + min(15, ((aqi - 300) / 200) * 15)  # 65–80

#     # Age bonus: smooth curve — very young and very old are most vulnerable
#     if age <= 5:
#         age_bonus = 20
#     elif age <= 12:
#         age_bonus = 20 - ((age - 5) / 7) * 8   # 20→12
#     elif age <= 18:
#         age_bonus = 12 - ((age - 12) / 6) * 9  # 12→3
#     elif age <= 40:
#         age_bonus = 3                            # healthy adult baseline
#     elif age <= 60:
#         age_bonus = 3 + ((age - 40) / 20) * 7  # 3→10
#     elif age <= 75:
#         age_bonus = 10 + ((age - 60) / 15) * 8 # 10→18
#     else:
#         age_bonus = 18 + min(7, ((age - 75) / 20) * 7) # 18→25

#     # Condition bonuses: scale with AQI severity (worse air = conditions matter more)
#     aqi_severity = min(1.0, aqi / 300)  # 0–1 scale
#     asthma_bonus = round(8 + aqi_severity * 12) if has_asthma else 0  # 8–20
#     heart_bonus  = round(6 + aqi_severity * 10) if has_heart  else 0  # 6–16

#     score = min(100, round(base + age_bonus + asthma_bonus + heart_bonus))

#     if score <= 20:
#         label   = "🟢 Low Risk"
#         color   = "#16a34a"
#         bgcolor = "#dcfce7"
#         advice  = [
#             "✅ Air quality is safe for your profile.",
#             "🏃 You can do normal outdoor activities.",
#             "💧 Stay hydrated and enjoy fresh air.",
#         ]
#     elif score <= 45:
#         label   = "🟡 Moderate Risk"
#         color   = "#ca8a04"
#         bgcolor = "#fef9c3"
#         advice  = [
#             "⚠️ Limit prolonged outdoor exposure.",
#             "😷 Carry your inhaler if you have one.",
#             "🪟 Keep windows closed during peak hours.",
#         ]
#     elif score <= 70:
#         label   = "🟠 High Risk"
#         color   = "#ea580c"
#         bgcolor = "#fff7ed"
#         advice  = [
#             "🚫 Avoid all non-essential outdoor activity.",
#             "😷 Wear N95 mask if going outside.",
#             "🧴 Run air purifier indoors continuously.",
#             "💊 Keep medications accessible.",
#         ]
#     else:
#         label   = "🔴 Very High Risk"
#         color   = "#dc2626"
#         bgcolor = "#fef2f2"
#         advice  = [
#             "🚨 Stay strictly indoors.",
#             "😷 Wear N95/N99 even indoors if possible.",
#             "🏥 Seek medical advice if any breathing difficulty.",
#             "👨‍👩‍👧 Especially dangerous for your age/condition.",
#         ]

#     return score, label, color, bgcolor, advice, age_bonus, asthma_bonus, heart_bonus


# # =========================================
# # FEATURE 2 HELPERS — 7-Day Forecast
# # =========================================
# def generate_forecast(current_aqi, raw, weather, city):
#     """
#     Hybrid AQI Forecast:
#     - Pollutant-based evolution (PM2.5, PM10, NO2)
#     - Weather-driven adjustments (wind, humidity, temp)
#     """

#     pm25 = raw.get("PM2.5", 0) or 0
#     pm10 = raw.get("PM10", 0) or 0
#     no2  = raw.get("NO2", 0) or 0

#     forecast = []
#     today = datetime.today()

#     seed = abs(hash(city.lower() + today.strftime("%Y%m%d"))) % (2**31)
#     rng = np.random.default_rng(seed)

#     prev_aqi = current_aqi

#     for i in range(7):

#         # -------- Pollutant evolution --------
#         pm25 *= rng.uniform(0.96, 1.04)
#         pm10 *= rng.uniform(0.97, 1.03)
#         no2  *= rng.uniform(0.90, 1.08)

#         # -------- Weather impact --------
#         wind = weather["wind"]
#         humidity = weather["humidity"]
#         temp = weather["temp"]

#         weather_effect = 0

#         if wind < 2:
#             weather_effect += 20
#         elif wind < 5:
#             weather_effect += 5
#         else:
#             weather_effect -= 15

#         if humidity > 75:
#             weather_effect += 8
#         elif humidity < 40:
#             weather_effect -= 5

#         if temp > 35:
#             weather_effect += 5

#         # Weekend cleaner air
#         day = (today + timedelta(days=i)).weekday()
#         if day >= 5:
#             weather_effect -= 10

#         # -------- AQI Calculation --------
#         base_aqi = max(pm25, pm10, no2)
#         aqi = base_aqi + weather_effect

#         # Smooth transition
#         aqi = 0.7 * prev_aqi + 0.3 * aqi

#         # Small natural noise
#         aqi += rng.uniform(-5, 5)

#         aqi = max(20, min(500, aqi))
#         prev_aqi = aqi

#         forecast.append({
#             "date": (today + timedelta(days=i)).strftime("%a\n%d %b"),
#             "aqi": round(aqi, 1)
#         })

#     return forecast

# def worst_day(forecast):
#     return max(forecast, key=lambda x: x["aqi"])

# def best_day(forecast):
#     return min(forecast, key=lambda x: x["aqi"])

# def forecast_color(aqi):
#     if aqi <= 50:    return "#00e600"
#     elif aqi <= 100: return "#9acd32"
#     elif aqi <= 200: return "#fbbf24"
#     elif aqi <= 300: return "#f97316"
#     elif aqi <= 400: return "#ef4444"
#     else:            return "#7f1d1d"


# # =========================================
# # FEATURE 3 HELPERS — Activity Planner
# # =========================================
# ACTIVITY_LIMITS = {
#     "🏃 Jogging / Running":   {"safe": 100, "risky": 200},
#     "🚴 Cycling":             {"safe": 100, "risky": 200},
#     "🧓 Elderly Walking":     {"safe":  50, "risky": 100},
#     "👦 Kids Outdoor Play":   {"safe":  50, "risky": 100},
#     "🧘 Yoga / Stretching":   {"safe": 150, "risky": 250},
#     "🏋️ Intense Gym Outdoor": {"safe":  75, "risky": 150},
# }

# def activity_advice(aqi, activity):
#     key    = activity
#     limits = ACTIVITY_LIMITS.get(key, {"safe": 100, "risky": 200})
#     name   = activity.split(" ", 1)[1] if " " in activity else activity
#     if aqi <= limits["safe"]:
#         return "safe",     f"✅ Safe to do **{name}** right now!"
#     elif aqi <= limits["risky"]:
#         return "moderate", f"⚠️ Moderate risk for **{name}**. Consider wearing a mask."
#     else:
#         return "unsafe",   f"🚫 **{name}** is not recommended outdoors today."

# def best_time_message(aqi):
#     if aqi <= 100:   return "🕕 Any time is fine. Morning (6–8 AM) is typically freshest."
#     elif aqi <= 200: return "🕔 Prefer early morning (5–7 AM) before traffic peaks."
#     else:            return "🚫 No outdoor time recommended today. Stay indoors."

# def hourly_heatmap(aqi, city=""):
#     """
#     Realistic hourly AQI pattern:
#     - Dual-peak model (morning & evening rush)
#     - Clean night trough (4–6 AM)
#     - Midday dip (photochemistry disperses pollutants)
#     - Smooth sinusoidal blending between peaks
#     - City-specific offset: coastal cities have better sea-breeze afternoons
#     """
#     coastal_cities = {"mumbai", "chennai", "kolkata", "visakhapatnam", "kochi"}
#     is_coastal = city.strip().lower() in coastal_cities

#     # Hourly multiplier profile (index = hour 0–23)
#     base_profile = [
#         0.72, 0.68, 0.65, 0.63, 0.62, 0.65,  # 0–5 AM: cleanest (low traffic)
#         0.80, 1.05, 1.28, 1.35, 1.22, 1.05,  # 6–11: morning rush + build-up
#         0.95, 0.88, 0.85, 0.88, 0.95, 1.20,  # 12–17: midday dip then rise
#         1.38, 1.42, 1.30, 1.12, 0.95, 0.80,  # 18–23: evening peak & taper
#     ]

#     if is_coastal:
#         # Sea breeze hits around 13–17, pushing pollutants inland
#         for h in range(13, 18):
#             base_profile[h] *= 0.85

#     hours = []
#     seed  = abs(hash(city.lower() + datetime.today().strftime("%Y%m%d"))) % (2**31)
#     rng   = np.random.default_rng(seed)

#     for h, factor in enumerate(base_profile):
#         # Small per-hour noise so bars aren't perfectly smooth (realistic)
#         jitter = rng.uniform(-0.03, 0.03)
#         est    = max(10, min(500, round(aqi * (factor + jitter))))
#         hours.append({"Hour": f"{h:02d}:00", "Est. AQI": est})

#     return hours


# # =========================================
# # SIDEBAR — Navigation
# # =========================================
# st.sidebar.markdown("""
# <style>
# .aqi-box{
#     background:#f3f4f6; padding:20px; border-radius:18px;
#     box-shadow:0 2px 8px rgba(0,0,0,.08);
# }
# .aqi-title{ font-size:22px; font-weight:bold; margin-bottom:14px; }
# .aqi-tag{
#     padding:10px 14px; border-radius:8px; font-weight:600;
#     margin-bottom:6px; color:white;
# }
# .good         { background:#00e600; }
# .satisfactory { background:#9acd32; color:black !important; }
# .moderate     { background:#fff000; color:black !important; }
# .poor         { background:#ff8800; }
# .verypoor     { background:#ff1a1a; }
# .severe       { background:#8b0029; }
# </style>

# <div class="aqi-box">
# <div class="aqi-title">🎨 AQI Scale</div>
# <div class="aqi-tag good">🙂 Good (0–50)</div>
# <div class="aqi-tag satisfactory">🙂 Satisfactory (51–100)</div>
# <div class="aqi-tag moderate">😐 Moderate (101–200)</div>
# <div class="aqi-tag poor">😷 Poor (201–300)</div>
# <div class="aqi-tag verypoor">🤢 Very Poor (301–400)</div>
# <div class="aqi-tag severe">☠️ Severe (401+)</div>
# </div>
# """, unsafe_allow_html=True)

# st.sidebar.markdown("---")
# st.sidebar.markdown("### 🔧 Features")

# # Radio acts as sidebar navigation for the 3 features
# feature = st.sidebar.radio(
#     "Select a feature to explore:",
#     options=[
#         "📊 AQI Monitor",
#         "👤 Personalized Health Risk",
#         "📅 7-Day AQI Forecast",
#         "🏃 Outdoor Activity Planner",
#     ],
#     key="sidebar_feature"
# )

# # Feature descriptions shown in sidebar
# descriptions = {
#     "📊 AQI Monitor": "Enter a city to get live AQI, pollutant breakdown, health advice, and weather.",
#     "👤 Personalized Health Risk": "Enter your age & health conditions to get a custom 0–100 risk score with detailed advice.",
#     "📅 7-Day AQI Forecast": "See a simulated 7-day AQI trend with worst/best day alerts and improving/worsening direction.",
#     "🏃 Outdoor Activity Planner": "Pick your activity (jogging, cycling, etc.) to see if today's AQI is safe + best time to go.",
# }
# st.sidebar.markdown(
#     f'<div class="sidebar-feature-info">ℹ️ {descriptions[feature]}</div>',
#     unsafe_allow_html=True
# )

# # =========================================
# # SIDEBAR — TELEGRAM ALERT BUTTON
# # =========================================
# st.sidebar.markdown("---")
# st.sidebar.markdown("### 📲 Telegram Alerts")
# st.sidebar.caption("Get instant AQI alert + daily updates at 8 AM on Telegram.")
# st.sidebar.markdown("""
# <div style='background:#f1f5f9;padding:10px;border-radius:8px;
# font-size:12px;color:#475569;margin-top:8px;'>

# 📌 <b>How to Subscribe:</b><br>
# 1. Click the button<br>
# 2. Open Telegram<br>
# 3. Press <b>Start</b><br>
# 4. Send: <b>/subscribe your_city</b>

# </div>
# """, unsafe_allow_html=True)

# # Session flag so we only show the button once per session
# if "telegram_subscribed" not in st.session_state:
#     st.session_state.telegram_subscribed = False

# def build_telegram_message(city_name, aqi_val, raw_data, weather_data):
#     """Builds a rich Telegram message with current AQI data."""
#     import pytz
#     from datetime import datetime
#     IST      = pytz.timezone("Asia/Kolkata")
#     now_ist  = datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST")

#     # Category
#     if aqi_val <= 50:    cat_label, cat_emoji = "Good ✅",          "🟢"
#     elif aqi_val <= 100: cat_label, cat_emoji = "Satisfactory 🙂",  "🟡"
#     elif aqi_val <= 200: cat_label, cat_emoji = "Moderate 😐",       "🟠"
#     elif aqi_val <= 300: cat_label, cat_emoji = "Poor 😷",           "🔴"
#     elif aqi_val <= 400: cat_label, cat_emoji = "Very Poor 🤢",      "🔴"
#     else:                cat_label, cat_emoji = "Severe ☠️",         "⚫"

#     # Advice
#     if aqi_val <= 50:
#         advice = ["✅ Air is clean. Enjoy outdoor activities.", "💧 Stay hydrated."]
#     elif aqi_val <= 100:
#         advice = ["😷 Sensitive groups wear a mask.", "🚶 Limit long outdoor stays."]
#     elif aqi_val <= 200:
#         advice = ["😷 Wear N95 mask outdoors.", "🏃 Avoid jogging 8–10 AM.", "🧴 Use air purifier."]
#     elif aqi_val <= 300:
#         advice = ["🏠 Stay indoors.", "😷 N95/N99 mask if going out.", "❌ Avoid outdoor exercise."]
#     else:
#         advice = ["🚨 Stay strictly indoors.", "😷 N99 mask even indoors.", "🏥 Seek help if breathing issues."]

#     # Best time
#     if aqi_val <= 100:   outdoor_time = "🕕 Any time is fine. Morning (6–8 AM) is freshest."
#     elif aqi_val <= 200: outdoor_time = "🕔 Early morning (5–7 AM) before traffic peaks."
#     else:                outdoor_time = "🚫 Not recommended to go outside today."

#     # Pollutants
#     pollutant_lines = ""
#     if raw_data:
#         for k, v in raw_data.items():
#             if v is not None:
#                 pollutant_lines += f"  • {k}: {v}\n"

#     # Weather
#     weather_lines = ""
#     if weather_data:
#         weather_lines = (
#             f"\n☁️ *Weather in {city_name}*\n"
#             f"  🌡 Temp: {weather_data['temp']}°C\n"
#             f"  💧 Humidity: {weather_data['humidity']}%\n"
#             f"  🌬 Wind: {weather_data['wind']} m/s\n"
#             f"  ⛅ Condition: {weather_data['condition']}\n"
#         )

#     msg = f"""🌫️ *AQI Alert — {city_name.upper()}*
# 📅 {now_ist}
# {'─' * 28}

# {cat_emoji} *AQI: {aqi_val}* — {cat_label}

# 💡 *Advice:*
# """ + "\n".join(f"  {t}" for t in advice) + f"""

# ⏰ *Best Outdoor Time:*
#   {outdoor_time}

# 🔬 *Pollutants:*
# {pollutant_lines}{weather_lines}
# {'─' * 28}
# 🔔 _You will now receive this alert daily at 8:00 AM IST._
# _Powered by AQI Monitor App_"""

#     return msg


# def send_telegram_alert(city_name, aqi_val, raw_data, weather_data):
#     """Sends the alert message via Telegram Bot API."""
#     msg = build_telegram_message(city_name, aqi_val, raw_data, weather_data)
#     url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
#     try:
#         res = requests.post(url, data={
#             "chat_id":    CHAT_ID,
#             "text":       msg,
#             "parse_mode": "Markdown",
#         }, timeout=15)
#         return res.status_code == 200, res.text
#     except Exception as e:
#         return False, str(e)


# # Show button only if AQI data is available
# if st.session_state.aqi_data is not None:
#     if not st.session_state.telegram_subscribed:
#         if st.sidebar.button(
#             "📩 Send Alert & Subscribe to Daily Updates",
#             use_container_width=True,
#             type="primary"
#         ):
#             with st.sidebar:
#                 with st.spinner("Sending alert to Telegram..."):
#                     ok, err = send_telegram_alert(
#                         st.session_state.aqi_data["city"],
#                         st.session_state.aqi_data["aqi"],
#                         st.session_state.aqi_data["raw"],
#                         st.session_state.aqi_data["weather"],
#                     )
#             if ok:
#                 st.session_state.telegram_subscribed = True
#                 st.sidebar.success("✅ Alert sent! Opening Telegram...")
#                 # Auto-open Telegram after 1 second
#                 st.sidebar.markdown(
#                     """
#                     <script>
#                     setTimeout(function(){
#                         window.open('https://t.me/aqi_alert_2026_bot', '_blank');
#                     }, 800);
#                     </script>
#                     """,
#                     unsafe_allow_html=True
#                 )
#                 # Fallback clickable link
#                 st.sidebar.markdown(
#                     "👉 [Open Telegram Bot](https://t.me/aqi_alert_2026_bot)",
#                     unsafe_allow_html=True
#                 )
#             else:
#                 st.sidebar.error(f"❌ Failed to send. Check bot token.\n{err}")
#     else:
#         # Already subscribed — show status
#         st.sidebar.markdown("""
#         <div style='background:#dcfce7;padding:12px;border-radius:10px;
#         border-left:4px solid #16a34a;font-size:13px;color:#166534;'>
#             ✅ <b>Subscribed!</b><br>
#             You'll receive daily AQI alerts at<br>
#             <b>8:00 AM IST</b> on Telegram.
#         </div>
#         """, unsafe_allow_html=True)
#         st.sidebar.markdown(
#             "👉 [Open Telegram Bot](https://t.me/aqi_alert_2026_bot)",
#             unsafe_allow_html=True
#         )
#         # Allow unsubscribe
#         if st.sidebar.button("🔕 Unsubscribe", use_container_width=True):
#             st.session_state.telegram_subscribed = False
#             st.sidebar.info("Unsubscribed from daily alerts.")
# else:
#     st.sidebar.markdown("""
#     <div style='background:#f1f5f9;padding:12px;border-radius:10px;
#     font-size:13px;color:#64748b;'>
#         🔍 Search a city first to enable Telegram alerts.
#     </div>
#     """, unsafe_allow_html=True)

# # =========================================
# # CITY INPUT — always visible at top
# # =========================================
# st.markdown("<h1 style='text-align:center;'>🌫️ AQI MONITOR</h1>", unsafe_allow_html=True)

# col_inp, col_btn = st.columns([4, 1])
# with col_inp:
#     city = st.text_input("Enter City", placeholder="Delhi, Mumbai, Chennai...", label_visibility="collapsed")
# with col_btn:
#     check = st.button("🔍 Check AQI", use_container_width=True)

# # On button click → fetch and store in session_state
# if check:
#     if city.strip():
#         with st.spinner(f"Fetching AQI for {city}..."):
#             raw, missing = fetch(city)
#             weather      = fetch_weather(city)
#         if not raw:
#             st.error("❌ City not found. Try a different spelling.")
#             st.session_state.aqi_data = None
#         else:
#             available = [v for v in raw.values() if v is not None]
#             aqi       = int(max(available))
#             st.session_state.aqi_data = {
#                 "raw":     raw,
#                 "aqi":     aqi,
#                 "city":    city,
#                 "weather": weather,
#             }
#     else:
#         st.warning("Please enter a city name.")

# # =========================================
# # RENDER — only if we have data
# # =========================================
# if st.session_state.aqi_data is None:
#     st.info("👆 Enter a city above and click **Check AQI** to begin.")
#     st.stop()

# # Unpack stored data
# raw     = st.session_state.aqi_data["raw"]
# aqi     = st.session_state.aqi_data["aqi"]
# city    = st.session_state.aqi_data["city"]
# weather = st.session_state.aqi_data["weather"]

# cat, text_color, bg = category(aqi)

# # =========================================================
# # PAGE: AQI MONITOR  (default view)
# # =========================================================
# if feature == "📊 AQI Monitor":

#     # AQI CARD
#     st.markdown(f"""
#     <style>
#     .dynamic-card{{
#         background:{bg}; padding:50px; border-radius:25px;
#         text-align:center; margin-top:10px; margin-bottom:20px;
#     }}
#     .aqi-number{{font-size:80px;font-weight:bold;color:{text_color};margin:10px 0;}}
#     .aqi-cat   {{font-size:32px;font-weight:600;color:{text_color};}}
#     </style>
#     """, unsafe_allow_html=True)

#     st.markdown(f"""
#     <div class="dynamic-card">
#         <h2>{city.upper()}</h2>
#         <div class="aqi-number">{aqi}</div>
#         <div class="aqi-cat">{cat}</div>
#     </div>
#     """, unsafe_allow_html=True)

#     # LIVE WEATHER
#     if weather:
#         st.markdown("## ☁️ Live Weather")
#         w1, w2, w3, w4 = st.columns(4)
#         w1.metric("Temperature", f"{weather['temp']} °C")
#         w2.metric("Humidity",    f"{weather['humidity']}%")
#         w3.metric("Wind Speed",  f"{weather['wind']} m/s")
#         w4.metric("Condition",   weather['condition'])
#         if weather["wind"] < 2:
#             st.warning("🌬️ Low wind speed — pollutants may be trapped near the surface.")
#         if weather["humidity"] > 70:
#             st.warning("💧 High humidity — may worsen respiratory symptoms.")

#     # SOLUTIONS
#     st.markdown("## 🛡️ Protective Measures")
#     tips = solutions(aqi)
#     c1, c2, c3, c4 = st.columns(4)
#     for col, tip in zip([c1, c2, c3, c4], tips):
#         col.markdown(f'<div class="solution">{tip}</div>', unsafe_allow_html=True)

#     # HEALTH
#     st.markdown("## ❤️ Health Challenges")
#     risks = health(aqi)
#     h1, h2, h3 = st.columns(3)
#     h1.markdown(f'<div class="health"><b>🫁 Respiratory</b><br><br>{risks[0]}</div>', unsafe_allow_html=True)
#     h2.markdown(f'<div class="health"><b>❤️ Heart</b><br><br>{risks[1]}</div>',       unsafe_allow_html=True)
#     h3.markdown(f'<div class="health"><b>🤧 Allergy</b><br><br>{risks[2]}</div>',     unsafe_allow_html=True)

#     # POLLUTANTS
#     st.markdown("## 📊 Pollutants")
#     df = pd.DataFrame(
#         [(k, v) for k, v in raw.items() if v is not None],
#         columns=["Pollutant", "Value"]
#     )
#     st.bar_chart(df.set_index("Pollutant"))

#     st.caption("💡 Use the **sidebar** to explore Personalized Health Risk, 7-Day Forecast, and Activity Planner.")


# # =========================================================
# # PAGE: PERSONALIZED HEALTH RISK
# # =========================================================
# elif feature == "👤 Personalized Health Risk":

#     st.markdown(f"""
#     <div style="background:{bg};padding:20px 30px;border-radius:18px;
#     margin-bottom:20px;text-align:center;">
#         <span style="font-size:18px;color:{text_color};font-weight:600;">
#             Current AQI in {city.upper()}: {aqi} — {cat}
#         </span>
#     </div>
#     """, unsafe_allow_html=True)

#     st.markdown("### Enter Your Health Profile")
#     st.caption("Your risk score is calculated from AQI + your personal health factors.")

#     with st.form("health_form"):
#         col_a, col_b, col_c = st.columns(3)
#         age        = col_a.number_input("Your Age", min_value=1, max_value=110, value=30)
#         has_asthma = col_b.checkbox("I have Asthma / Respiratory condition")
#         has_heart  = col_c.checkbox("I have a Heart condition")
#         submitted  = st.form_submit_button("🧮 Calculate My Risk", use_container_width=True)

#     if submitted:
#         score, label, color, bgcolor, advice_list, age_bonus, asthma_bonus, heart_bonus = \
#             personal_risk_score(aqi, age, has_asthma, has_heart)

#         # SCORE GAUGE
#         st.markdown(f"""
#         <div class="risk-box" style="background:{bgcolor};color:{color};border:2px solid {color};">
#             {label} &nbsp;|&nbsp; Risk Score: {score} / 100
#         </div>
#         """, unsafe_allow_html=True)

#         # PROGRESS BAR
#         st.progress(score / 100)

#         # DETAILED ADVICE
#         st.markdown("#### 📋 Personalised Advice for You")
#         for tip in advice_list:
#             st.markdown(f"- {tip}")

#         # SCORE BREAKDOWN
#         with st.expander("🔍 See how your score was calculated", expanded=True):
#             aqi_contrib = round(score - age_bonus - asthma_bonus - heart_bonus)
#             rows = [
#                 {"Factor": "AQI Level", "Points Added": aqi_contrib,
#                  "Reason": f"AQI {aqi} → base risk (linear interpolation)"},
#             ]
#             age_bonus_r = round(age_bonus)
#             if age_bonus_r > 0:
#                 if age <= 12:
#                     reason = "Children have developing lungs"
#                 elif age <= 18:
#                     reason = "Adolescent — slightly elevated sensitivity"
#                 elif age <= 40:
#                     reason = "Healthy adult baseline"
#                 elif age <= 60:
#                     reason = "Mild age-related vulnerability increase"
#                 elif age <= 75:
#                     reason = "Elevated vulnerability with age"
#                 else:
#                     reason = "Elderly — high respiratory/cardiac sensitivity"
#                 rows.append({"Factor": f"Age {age}", "Points Added": age_bonus_r,
#                              "Reason": reason})
#             if has_asthma:
#                 rows.append({"Factor": "Asthma / Respiratory", "Points Added": asthma_bonus,
#                              "Reason": f"Pollutants trigger asthma (scaled with AQI severity)"})
#             if has_heart:
#                 rows.append({"Factor": "Heart Condition", "Points Added": heart_bonus,
#                              "Reason": "Fine particles strain the heart"})
#             rows.append({"Factor": "**TOTAL**", "Points Added": score, "Reason": "Capped at 100"})
#             st.table(pd.DataFrame(rows))

#         # COMPARISON WITH GENERAL POPULATION
#         st.markdown("#### 👥 How Does Your Risk Compare?")
#         comp_col1, comp_col2, comp_col3 = st.columns(3)
#         general_score, *_ = personal_risk_score(aqi, 30, False, False)
#         comp_col1.metric("General Public", f"{general_score}/100")
#         comp_col2.metric("Your Score", f"{score}/100",
#                          delta=f"+{score - general_score}" if score > general_score else f"{score - general_score}")
#         comp_col3.metric("Max Possible", "100/100")


# # =========================================================
# # PAGE: 7-DAY AQI FORECAST
# # =========================================================
# elif feature == "📅 7-Day AQI Forecast":

#     st.markdown(f"""
#     <div style="background:{bg};padding:20px 30px;border-radius:18px;
#     margin-bottom:20px;text-align:center;">
#         <span style="font-size:18px;color:{text_color};font-weight:600;">
#             Current AQI in {city.upper()}: {aqi} — {cat}
#         </span>
#     </div>
#     """, unsafe_allow_html=True)

#     if weather is None:
#        st.warning("⚠️ Weather data unavailable — using default values.")
#        weather = {"temp": 25, "humidity": 50, "wind": 2}

#     forecast = generate_forecast(aqi, raw, weather, city)
#     w_day    = worst_day(forecast)
#     b_day    = best_day(forecast)

#     # ALERT ROW
#     alert_col1, alert_col2 = st.columns(2)
#     w_cat, _, _ = category(int(w_day["aqi"]))
#     b_cat, _, _ = category(int(b_day["aqi"]))
#     alert_col1.error(
#         f"⚠️ **Worst day:** {w_day['date'].replace(chr(10),' ')} "
#         f"— AQI {w_day['aqi']} ({w_cat})"
#     )
#     alert_col2.success(
#         f"✅ **Best day:** {b_day['date'].replace(chr(10),' ')} "
#         f"— AQI {b_day['aqi']} ({b_cat})"
#     )

#     # 7 FORECAST CARDS
#     st.markdown("### 📆 Day-by-Day Forecast")
#     fcols = st.columns(7)
#     for col, day in zip(fcols, forecast):
#         day_aqi   = day["aqi"]
#         day_color = forecast_color(day_aqi)
#         d_cat, d_text, d_bg = category(int(day_aqi))
#         col.markdown(f"""
#         <div class="forecast-card" style="border-top:4px solid {day_color};">
#             <div style="font-size:11px;color:#555;font-weight:600;white-space:pre-line;">
#                 {day['date']}
#             </div>
#             <div style="font-size:26px;font-weight:bold;color:{day_color};margin:8px 0;">
#                 {int(day_aqi)}
#             </div>
#             <div style="font-size:9px;color:{day_color};font-weight:700;letter-spacing:.5px;">
#                 {d_cat}
#             </div>
#         </div>
#         """, unsafe_allow_html=True)

#     # LINE CHART
#     st.markdown("### 📈 AQI Trend Chart")
#     forecast_df = pd.DataFrame({
#         "Date": [d["date"].replace("\n", " ") for d in forecast],
#         "AQI":  [d["aqi"] for d in forecast]
#     }).set_index("Date")
#     st.line_chart(forecast_df, use_container_width=True)

#     # TREND VERDICT
#     first_aqi = forecast[0]["aqi"]
#     last_aqi  = forecast[-1]["aqi"]
#     st.markdown("### 🧭 Trend Direction")
#     if last_aqi > first_aqi * 1.1:
#         st.error("📈 AQI is trending **WORSE** over the next 7 days. Prepare precautions.")
#     elif last_aqi < first_aqi * 0.9:
#         st.success("📉 AQI is trending **BETTER** over the next 7 days. Conditions improving!")
#     else:
#         st.info("➡️ AQI is expected to remain **STABLE** over the next 7 days.")

#     # SAFE DAY SUMMARY TABLE
#     st.markdown("### 🗓️ Weekly Summary Table")
#     summary = []
#     for day in forecast:
#         d_cat, _, _ = category(int(day["aqi"]))
#         safe_icon = "✅" if day["aqi"] <= 100 else ("⚠️" if day["aqi"] <= 200 else "🚫")
#         summary.append({
#             "Day":          day["date"].replace("\n", " "),
#             "Est. AQI":     int(day["aqi"]),
#             "Category":     d_cat,
#             "Safe Outdoor": safe_icon,
#         })
#     st.table(pd.DataFrame(summary))

#     st.caption("ℹ️ Forecast is simulated based on current AQI with realistic daily variation.")


# # =========================================================
# # PAGE: OUTDOOR ACTIVITY PLANNER
# # =========================================================
# elif feature == "🏃 Outdoor Activity Planner":

#     st.markdown(f"""
#     <div style="background:{bg};padding:20px 30px;border-radius:18px;
#     margin-bottom:20px;text-align:center;">
#         <span style="font-size:18px;color:{text_color};font-weight:600;">
#             Current AQI in {city.upper()}: {aqi} — {cat}
#         </span>
#     </div>
#     """, unsafe_allow_html=True)

#     # ACTIVITY PICKER
#     st.markdown("### 🎯 Select Your Activity")
#     activity = st.selectbox(
#         "What are you planning to do?",
#         list(ACTIVITY_LIMITS.keys()),
#         key="activity_select"
#     )

#     status, act_msg = activity_advice(aqi, activity)
#     best_time       = best_time_message(aqi)

#     # RESULT CARD
#     st.markdown("### 🚦 Today's Recommendation")
#     if status == "safe":
#         st.markdown(f'<div class="activity-card" style="font-size:18px;">{act_msg}</div>',
#                     unsafe_allow_html=True)
#     elif status == "moderate":
#         st.markdown(f'<div class="activity-warn" style="font-size:18px;">{act_msg}</div>',
#                     unsafe_allow_html=True)
#     else:
#         st.error(act_msg)

#     # BEST TIME BOX
#     st.markdown(f"""
#     <div class="forecast-card" style="margin-top:12px;padding:20px;">
#         <div style="font-size:16px;font-weight:700;margin-bottom:8px;">⏰ Best Time to Go Outside Today</div>
#         <div style="font-size:15px;color:#374151;">{best_time}</div>
#     </div>
#     """, unsafe_allow_html=True)

#     # HOURLY AQI ESTIMATE
    
#     hourly = hourly_heatmap(aqi, city)
#     # BEST HOURS TABLE
#     # best_hours = sorted(hourly, key=lambda x: x["Est. AQI"])[:5]
#     # st.markdown("#### 🏆 5 Best Hours Today")
#     # st.table(pd.DataFrame(best_hours))

#     # ALL ACTIVITIES TABLE
#     st.markdown("### 📋 All Activities — Today's AQI Safety")
#     rows = []
#     for act in ACTIVITY_LIMITS:
#         s, msg = activity_advice(aqi, act)
#         emoji  = "✅ Safe" if s == "safe" else ("⚠️ Moderate" if s == "moderate" else "🚫 Unsafe")
#         rows.append({
#             "Activity": act,
#             "Status":   emoji,
#             "Safe AQI Limit":  f"≤ {ACTIVITY_LIMITS[act]['safe']}",
#             "Risky AQI Limit": f"≤ {ACTIVITY_LIMITS[act]['risky']}",
#         })
#     st.table(pd.DataFrame(rows))

###################################################################################################

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
    # AQI base: linear interpolation within each band for smooth progression
    if aqi <= 50:
        base = 5 + (aqi / 50) * 10           # 5–15
    elif aqi <= 100:
        base = 15 + ((aqi - 50) / 50) * 15   # 15–30
    elif aqi <= 200:
        base = 30 + ((aqi - 100) / 100) * 20 # 30–50
    elif aqi <= 300:
        base = 50 + ((aqi - 200) / 100) * 15 # 50–65
    else:
        base = 65 + min(15, ((aqi - 300) / 200) * 15)  # 65–80

    # Age bonus: smooth curve — very young and very old are most vulnerable
    if age <= 5:
        age_bonus = 20
    elif age <= 12:
        age_bonus = 20 - ((age - 5) / 7) * 8   # 20→12
    elif age <= 18:
        age_bonus = 12 - ((age - 12) / 6) * 9  # 12→3
    elif age <= 40:
        age_bonus = 3                            # healthy adult baseline
    elif age <= 60:
        age_bonus = 3 + ((age - 40) / 20) * 7  # 3→10
    elif age <= 75:
        age_bonus = 10 + ((age - 60) / 15) * 8 # 10→18
    else:
        age_bonus = 18 + min(7, ((age - 75) / 20) * 7) # 18→25

    # Condition bonuses: scale with AQI severity (worse air = conditions matter more)
    aqi_severity = min(1.0, aqi / 300)  # 0–1 scale
    asthma_bonus = round(8 + aqi_severity * 12) if has_asthma else 0  # 8–20
    heart_bonus  = round(6 + aqi_severity * 10) if has_heart  else 0  # 6–16

    score = min(100, round(base + age_bonus + asthma_bonus + heart_bonus))

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
def generate_forecast(current_aqi, raw, weather, city):
    """
    Hybrid AQI Forecast:
    - Pollutant-based evolution (PM2.5, PM10, NO2)
    - Weather-driven adjustments (wind, humidity, temp)
    """

    pm25 = raw.get("PM2.5", 0) or 0
    pm10 = raw.get("PM10", 0) or 0
    no2  = raw.get("NO2", 0) or 0

    forecast = []
    today = datetime.today()

    seed = abs(hash(city.lower() + today.strftime("%Y%m%d"))) % (2**31)
    rng = np.random.default_rng(seed)

    prev_aqi = current_aqi

    for i in range(7):

        # -------- Pollutant evolution --------
        pm25 *= rng.uniform(0.96, 1.04)
        pm10 *= rng.uniform(0.97, 1.03)
        no2  *= rng.uniform(0.90, 1.08)

        # -------- Weather impact --------
        wind = weather["wind"]
        humidity = weather["humidity"]
        temp = weather["temp"]

        weather_effect = 0

        if wind < 2:
            weather_effect += 20
        elif wind < 5:
            weather_effect += 5
        else:
            weather_effect -= 15

        if humidity > 75:
            weather_effect += 8
        elif humidity < 40:
            weather_effect -= 5

        if temp > 35:
            weather_effect += 5

        # Weekend cleaner air
        day = (today + timedelta(days=i)).weekday()
        if day >= 5:
            weather_effect -= 10

        # -------- AQI Calculation --------
        base_aqi = max(pm25, pm10, no2)
        aqi = base_aqi + weather_effect

        # Smooth transition
        aqi = 0.7 * prev_aqi + 0.3 * aqi

        # Small natural noise
        aqi += rng.uniform(-5, 5)

        aqi = max(20, min(500, aqi))
        prev_aqi = aqi

        forecast.append({
            "date": (today + timedelta(days=i)).strftime("%a\n%d %b"),
            "aqi": round(aqi, 1)
        })

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

def hourly_heatmap(aqi, city=""):
    """
    Realistic hourly AQI pattern:
    - Dual-peak model (morning & evening rush)
    - Clean night trough (4–6 AM)
    - Midday dip (photochemistry disperses pollutants)
    - Smooth sinusoidal blending between peaks
    - City-specific offset: coastal cities have better sea-breeze afternoons
    """
    coastal_cities = {"mumbai", "chennai", "kolkata", "visakhapatnam", "kochi"}
    is_coastal = city.strip().lower() in coastal_cities

    # Hourly multiplier profile (index = hour 0–23)
    base_profile = [
        0.72, 0.68, 0.65, 0.63, 0.62, 0.65,  # 0–5 AM: cleanest (low traffic)
        0.80, 1.05, 1.28, 1.35, 1.22, 1.05,  # 6–11: morning rush + build-up
        0.95, 0.88, 0.85, 0.88, 0.95, 1.20,  # 12–17: midday dip then rise
        1.38, 1.42, 1.30, 1.12, 0.95, 0.80,  # 18–23: evening peak & taper
    ]

    if is_coastal:
        # Sea breeze hits around 13–17, pushing pollutants inland
        for h in range(13, 18):
            base_profile[h] *= 0.85

    hours = []
    seed  = abs(hash(city.lower() + datetime.today().strftime("%Y%m%d"))) % (2**31)
    rng   = np.random.default_rng(seed)

    for h, factor in enumerate(base_profile):
        # Small per-hour noise so bars aren't perfectly smooth (realistic)
        jitter = rng.uniform(-0.03, 0.03)
        est    = max(10, min(500, round(aqi * (factor + jitter))))
        hours.append({"Hour": f"{h:02d}:00", "Est. AQI": est})

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
st.sidebar.markdown("""
<div style='background:#f1f5f9;padding:10px;border-radius:8px;
font-size:12px;color:#475569;margin-top:8px;'>

📌 <b>How to Subscribe:</b><br>
1. Click the button<br>
2. Open Telegram<br>
3. Press <b>Start</b><br>
4. Send: <b>/subscribe your_city</b>

</div>
""", unsafe_allow_html=True)

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
    """Sends the rich alert to ALL subscribers from subscriptions.json.
    Falls back to CHAT_ID env var if the file is empty / missing."""
    import json
    msg = build_telegram_message(city_name, aqi_val, raw_data, weather_data)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    # Load all subscribers
    try:
        with open("subscriptions.json", "r") as f:
            users = json.load(f)
    except Exception:
        users = {}

    # Always include the env-var CHAT_ID as a fallback so the button
    # always reaches at least one person even before anyone subscribes via bot
    if CHAT_ID:
        users[str(CHAT_ID)] = city_name  # city doesn't matter here; we use city_name param

    if not users:
        return False, "No subscribers found and CHAT_ID not set."

    any_ok = False
    last_err = ""
    for chat_id, _city in users.items():
        try:
            res = requests.post(url, data={
                "chat_id":    chat_id,
                "text":       msg,
                "parse_mode": "Markdown",
            }, timeout=15)
            if res.status_code == 200:
                any_ok = True
            else:
                last_err = res.text
        except Exception as e:
            last_err = str(e)

    return any_ok, last_err


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
            aqi_contrib = round(score - age_bonus - asthma_bonus - heart_bonus)
            rows = [
                {"Factor": "AQI Level", "Points Added": aqi_contrib,
                 "Reason": f"AQI {aqi} → base risk (linear interpolation)"},
            ]
            age_bonus_r = round(age_bonus)
            if age_bonus_r > 0:
                if age <= 12:
                    reason = "Children have developing lungs"
                elif age <= 18:
                    reason = "Adolescent — slightly elevated sensitivity"
                elif age <= 40:
                    reason = "Healthy adult baseline"
                elif age <= 60:
                    reason = "Mild age-related vulnerability increase"
                elif age <= 75:
                    reason = "Elevated vulnerability with age"
                else:
                    reason = "Elderly — high respiratory/cardiac sensitivity"
                rows.append({"Factor": f"Age {age}", "Points Added": age_bonus_r,
                             "Reason": reason})
            if has_asthma:
                rows.append({"Factor": "Asthma / Respiratory", "Points Added": asthma_bonus,
                             "Reason": f"Pollutants trigger asthma (scaled with AQI severity)"})
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

    if weather is None:
       st.warning("⚠️ Weather data unavailable — using default values.")
       weather = {"temp": 25, "humidity": 50, "wind": 2}

    forecast = generate_forecast(aqi, raw, weather, city)
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

    # ── ACTIVITY PICKER ──────────────────────────────────────────────────────
    st.markdown("### 🎯 Select Your Activity")
    activity = st.selectbox(
        "What are you planning to do?",
        list(ACTIVITY_LIMITS.keys()),
        key="activity_select"
    )

    status, act_msg = activity_advice(aqi, activity)
    hourly          = hourly_heatmap(aqi, city)

    # ── TODAY'S RECOMMENDATION ───────────────────────────────────────────────
    st.markdown("### 🚦 Today's Recommendation")
    if status == "safe":
        st.markdown(f'<div class="activity-card" style="font-size:18px;">{act_msg}</div>',
                    unsafe_allow_html=True)
    elif status == "moderate":
        st.markdown(f'<div class="activity-warn" style="font-size:18px;">{act_msg}</div>',
                    unsafe_allow_html=True)
    else:
        st.error(act_msg)

    # ── SMART WINDOW PLANNER ─────────────────────────────────────────────────
    # st.markdown("### 🪟 Smart Window-Opening Planner")
    # st.caption("Should you open your windows right now? Based on inside vs outside AQI estimate.")
    # indoor_aqi_est = max(10, int(aqi * 0.6))  # typical indoor with closed windows
    # col_in, col_out = st.columns(2)
    # col_in.metric("🏠 Estimated Indoor AQI", indoor_aqi_est, help="With windows closed (estimated)")
    # col_out.metric("🌳 Current Outdoor AQI",  aqi,           help="Live from AQI sensor")
    # if aqi < indoor_aqi_est:
    #     st.success("✅ **Open your windows!** Outside air is cleaner than inside right now.")
    # elif aqi <= indoor_aqi_est * 1.2:
    #     st.info("🔄 Air quality is similar indoors and outdoors. Your call.")
    # else:
    #     st.warning("🚪 **Keep windows closed.** Outside air is significantly worse than inside.")

    # ── EXPOSURE DURATION CALCULATOR ─────────────────────────────────────────
    st.markdown("### ⏱️ How Long Can You Stay Outside Safely?")
    st.caption("Based on your activity intensity and current AQI.")
    intensity_map = {
        "🏃 Jogging / Running":   "high",
        "🚴 Cycling":             "high",
        "🧓 Elderly Walking":     "low",
        "👦 Kids Outdoor Play":   "low",
        "🧘 Yoga / Stretching":   "medium",
        "🏋️ Intense Gym Outdoor": "high",
    }
    intensity = intensity_map.get(activity, "medium")
    # Breathing multiplier: high intensity = 3× more air inhaled
    multiplier = {"high": 3.0, "medium": 1.8, "low": 1.0}[intensity]
    # Safe exposure: base of 120 min at AQI=50 good air, scales down with AQI
    if aqi <= 50:
        base_minutes = 120
    elif aqi <= 100:
        base_minutes = 90
    elif aqi <= 150:
        base_minutes = 60
    elif aqi <= 200:
        base_minutes = 30
    elif aqi <= 300:
        base_minutes = 15
    else:
        base_minutes = 0

    safe_minutes = max(0, int(base_minutes / multiplier))

    if safe_minutes == 0:
        st.error("🚫 **0 minutes recommended.** AQI is dangerously high. Stay indoors.")
    elif safe_minutes <= 15:
        st.warning(f"⚠️ **Maximum {safe_minutes} minutes** outside for this activity at current AQI.")
    elif safe_minutes <= 45:
        st.info(f"🕒 **Up to {safe_minutes} minutes** is acceptable. Take breaks.")
    else:
        st.success(f"✅ **Up to {safe_minutes} minutes** is safe for this activity today.")

    # ── MASK RECOMMENDATION ENGINE ────────────────────────────────────────────
    st.markdown("### 😷 Mask Recommendation")
    act_name = activity.split(" ", 1)[1] if " " in activity else activity
    mask_cols = st.columns(3)
    masks = [
        ("No Mask",    "No protection. Only suitable for AQI < 50.",       aqi <= 50,        "#dcfce7", "#166534"),
        ("Surgical",   "Filters large particles. OK for AQI 50–100.",       aqi <= 100,       "#fef9c3", "#854d0e"),
        ("N95 / FFP2", "Filters 95% of fine particles. For AQI 100–300.",   100 < aqi <= 300, "#fff7ed", "#9a3412"),
        ("N99 / P100",  "Maximum protection. For AQI > 300.",               aqi > 300,        "#fef2f2", "#991b1b"),
    ]
    recommended_mask = next((m for m in masks if m[2]), masks[-1])
    for i, (name, desc, _, bg_c, tc) in enumerate(masks[:3]):
        border = "3px solid " + tc if name == recommended_mask[0] else "1px solid #e5e7eb"
        star   = " ⭐ Recommended" if name == recommended_mask[0] else ""
        mask_cols[i].markdown(f"""
        <div style="background:{bg_c};border:{border};border-radius:12px;
        padding:14px;text-align:center;min-height:100px;">
            <div style="font-size:13px;font-weight:700;color:{tc};">{name}{star}</div>
            <div style="font-size:11px;color:{tc};margin-top:6px;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
    if aqi > 300:
        st.error("🚨 N99 / P100 mask strongly recommended. AQI is at POOR/SEVERE level.")

    # ── ACTIVITY-SPECIFIC HEALTH TIPS ─────────────────────────────────────────
    st.markdown("### 💡 Activity-Specific Health Tips")
    tips_map = {
        "🏃 Jogging / Running": [
            "🫁 Breathe through your nose — it filters more particles than mouth breathing.",
            "🕕 Run before 7 AM or after 8 PM to avoid traffic pollution peaks.",
            "💧 Drink water before & after — dehydration worsens pollutant absorption.",
            "📍 Choose parks & tree-lined routes — avoid main roads and intersections.",
        ],
        "🚴 Cycling": [
            "🛡️ Wear a close-fitting N95 mask — cyclists inhale 2× more air than walkers.",
            "🚦 Avoid busy roads — pollution near traffic is 3–5× worse than side streets.",
            "🧤 Cover your skin — some pollutants absorb through skin on long rides.",
            "⏸️ Stop at red lights and hold breath briefly — idling engines spike pollution.",
        ],
        "🧓 Elderly Walking": [
            "🐢 Walk slowly — lower exertion means less air intake and lower exposure.",
            "🌳 Stick to green areas — trees absorb PM2.5 and cool the air.",
            "🧣 Wear a light scarf around nose/mouth if no mask is available.",
            "🏥 Carry your medications — cold/dry air can trigger respiratory issues.",
        ],
        "👦 Kids Outdoor Play": [
            "👨‍👩‍👧 Supervise playtime — kids breathe 50% more air per kg than adults.",
            "🧸 Prefer shaded areas — UV + ozone combination worsens air at ground level.",
            "🧼 Wash hands & face immediately after outdoor play.",
            "⏰ Keep play sessions short (under 30 min) on moderate AQI days.",
        ],
        "🧘 Yoga / Stretching": [
            "🌬️ Deep breathing during yoga increases pollutant intake — choose indoor yoga if AQI > 150.",
            "🧘 Morning outdoor yoga is fine on low-AQI days — avoid evenings in winter.",
            "🌿 Face away from roads — even a few metres makes a measurable difference.",
            "💨 A gentle breeze is good; strong winds may carry more dust particles.",
        ],
        "🏋️ Intense Gym Outdoor": [
            "🚫 Not recommended outdoors if AQI > 100 — move to an indoor gym.",
            "💪 High-intensity exercise = 5× more air inhaled — exposure risk multiplies.",
            "🌡️ Heat + poor AQI = double stress on your cardiovascular system.",
            "🧊 Cool down indoors after training to avoid continued outdoor exposure.",
        ],
    }
    tips_list = tips_map.get(activity, ["Stay informed and listen to your body."])
    for tip in tips_list:
        st.markdown(f"- {tip}")

    # ── WEATHER IMPACT PANEL ──────────────────────────────────────────────────
    if weather:
        st.markdown("### 🌦️ How Today's Weather Affects Your Activity")
        wc1, wc2, wc3 = st.columns(3)
        # Wind
        wind_val = weather["wind"]
        if wind_val < 1.5:
            wind_verdict = ("🔴 Stagnant air", "Pollutants trapped near ground. Avoid outdoor exercise.")
        elif wind_val < 4:
            wind_verdict = ("🟡 Light breeze", "Some dispersion. Moderate outdoor activity OK.")
        else:
            wind_verdict = ("🟢 Good wind", "Pollutants dispersing well. Better for outdoor activity.")
        wc1.markdown(f"""
        <div style="background:#f5f7fb;padding:16px;border-radius:12px;text-align:center;">
            <div style="font-weight:700;">🌬️ Wind {weather['wind']} m/s</div>
            <div style="font-size:13px;margin-top:6px;color:#374151;">{wind_verdict[0]}<br>{wind_verdict[1]}</div>
        </div>
        """, unsafe_allow_html=True)
        # Humidity
        hum = weather["humidity"]
        if hum > 75:
            hum_verdict = ("🔴 High humidity", "Fine particles swell and penetrate deeper into lungs.")
        elif hum > 50:
            hum_verdict = ("🟡 Moderate humidity", "Mild effect on pollutant absorption.")
        else:
            hum_verdict = ("🟢 Low humidity", "Less particle swelling. Better for breathing.")
        wc2.markdown(f"""
        <div style="background:#f5f7fb;padding:16px;border-radius:12px;text-align:center;">
            <div style="font-weight:700;">💧 Humidity {hum}%</div>
            <div style="font-size:13px;margin-top:6px;color:#374151;">{hum_verdict[0]}<br>{hum_verdict[1]}</div>
        </div>
        """, unsafe_allow_html=True)
        # Temp
        temp = weather["temp"]
        if temp > 35:
            temp_verdict = ("🔴 Very hot", "Heat stress + pollution = double strain on heart & lungs.")
        elif temp > 28:
            temp_verdict = ("🟡 Warm", "Drink more water. Sweat opens pores to more absorption.")
        elif temp > 15:
            temp_verdict = ("🟢 Comfortable", "Good temperature for outdoor activity.")
        else:
            temp_verdict = ("🔵 Cold", "Cold air constricts airways. Extra care for asthma.")
        wc3.markdown(f"""
        <div style="background:#f5f7fb;padding:16px;border-radius:12px;text-align:center;">
            <div style="font-weight:700;">🌡️ Temp {temp}°C</div>
            <div style="font-size:13px;margin-top:6px;color:#374151;">{temp_verdict[0]}<br>{temp_verdict[1]}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── NEARBY INDOOR ALTERNATIVE SUGGESTIONS ─────────────────────────────────
    st.markdown("### 🏢 Can't Go Outside? Indoor Alternatives")
    alt_map = {
        "🏃 Jogging / Running":   ("🏃 Treadmill at gym / home", "🧗 Indoor climbing wall", "💃 Dance workout video"),
        "🚴 Cycling":             ("🚴 Stationary bike / spin class", "🏸 Badminton indoors", "🤸 HIIT workout"),
        "🧓 Elderly Walking":     ("🚶 Mall walking (air-conditioned)", "🧘 Chair yoga", "🌀 Indoor tai chi"),
        "👦 Kids Outdoor Play":   ("🎨 Arts & crafts indoors", "🧩 Board games", "💃 Indoor dance class"),
        "🧘 Yoga / Stretching":   ("🧘 Online yoga class", "🛀 Meditation + breathing", "🌿 Indoor plant care"),
        "🏋️ Intense Gym Outdoor": ("🏋️ Indoor gym session", "🥊 Boxing / martial arts studio", "🏊 Indoor swimming"),
    }
    alts = alt_map.get(activity, ("🏃 Indoor workout", "🧘 Meditation", "🎯 Home exercise"))
    a1, a2, a3 = st.columns(3)
    for col, alt in zip([a1, a2, a3], alts):
        col.markdown(f"""
        <div style="background:#f0f9ff;border:1px solid #bae6fd;border-radius:12px;
        padding:14px;text-align:center;font-weight:600;color:#0369a1;">
            {alt}
        </div>
        """, unsafe_allow_html=True)

    # ── ALL ACTIVITIES SAFETY TABLE (kept, it's useful) ─────────────────────
    st.markdown("### 📋 All Activities — Today's AQI Safety")
    rows = []
    for act in ACTIVITY_LIMITS:
        s, msg_txt = activity_advice(aqi, act)
        emoji  = "✅ Safe" if s == "safe" else ("⚠️ Moderate" if s == "moderate" else "🚫 Unsafe")
        rows.append({
            "Activity": act,
            "Status":   emoji,
            "Safe AQI Limit":  f"≤ {ACTIVITY_LIMITS[act]['safe']}",
            "Risky AQI Limit": f"≤ {ACTIVITY_LIMITS[act]['risky']}",
        })
    st.table(pd.DataFrame(rows))