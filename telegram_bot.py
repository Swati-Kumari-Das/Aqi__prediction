# """
# telegram_bot.py
# ---------------
# Runs as a SEPARATE background worker on Render.
# Sends a daily AQI alert to Telegram at 8:00 AM IST every day.

# Deploy as a "Background Worker" service on Render (not a Web Service).
# Command: python telegram_bot.py
# """

# import requests
# import schedule
# import time
# from datetime import datetime
# import pytz
# import os
# from dotenv import load_dotenv


# load_dotenv()

# # =========================================
# # CONFIG — replace with your values
# # =========================================
# BOT_TOKEN = os.getenv("BOT_TOKEN")
# CHAT_ID = os.getenv("CHAT_ID")
# AQICN_API = os.getenv("AQICN_API_KEY")
# OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")

# # Cities to monitor — add/remove as needed
# CITIES = ["Delhi", "Mumbai", "Bangalore"]

# IST = pytz.timezone("Asia/Kolkata")


# # =========================================
# # FETCH AQI
# # =========================================
# def fetch_aqi(city):
#     try:
#         url = f"https://api.waqi.info/feed/{city}/?token={AQICN_API}"
#         res = requests.get(url, timeout=10).json()
#         if res["status"] != "ok":
#             return None, None
#         iaqi = res["data"]["iaqi"]
#         raw = {
#             "PM2.5": iaqi.get("pm25", {}).get("v"),
#             "PM10":  iaqi.get("pm10", {}).get("v"),
#             "NO2":   iaqi.get("no2",  {}).get("v"),
#             "SO2":   iaqi.get("so2",  {}).get("v"),
#             "CO":    iaqi.get("co",   {}).get("v"),
#             "O3":    iaqi.get("o3",   {}).get("v"),
#         }
#         vals = [v for v in raw.values() if v is not None]
#         if not vals:
#             return None, None
#         return int(max(vals)), raw
#     except Exception as e:
#         print(f"[fetch_aqi] Error for {city}: {e}")
#         return None, None


# # =========================================
# # AQI HELPERS
# # =========================================
# def category(aqi):
#     if aqi <= 50:    return "Good ✅",         "🟢"
#     elif aqi <= 100: return "Satisfactory 🙂",  "🟡"
#     elif aqi <= 200: return "Moderate 😐",       "🟠"
#     elif aqi <= 300: return "Poor 😷",           "🔴"
#     elif aqi <= 400: return "Very Poor 🤢",      "🔴"
#     else:            return "Severe ☠️",          "⚫"

# def get_advice(aqi):
#     if aqi <= 50:
#         return [
#             "✅ Air quality is good.",
#             "🏃 Safe for all outdoor activities.",
#             "💧 Stay hydrated.",
#         ]
#     elif aqi <= 100:
#         return [
#             "😷 Sensitive groups should wear a mask.",
#             "🚶 Limit prolonged outdoor exposure.",
#             "🪟 Keep windows closed during peak hours.",
#         ]
#     elif aqi <= 200:
#         return [
#             "😷 Wear N95 mask outdoors.",
#             "🏃 Avoid jogging between 8–10 AM.",
#             "🧴 Run air purifier indoors.",
#         ]
#     elif aqi <= 300:
#         return [
#             "🏠 Stay indoors as much as possible.",
#             "😷 Wear N95/N99 mask if going out.",
#             "🧴 Run purifier continuously.",
#             "❌ Avoid all outdoor exercise.",
#         ]
#     else:
#         return [
#             "🚨 SEVERE: Stay strictly indoors.",
#             "😷 Wear N99 mask even indoors.",
#             "👨‍👩‍👧 Protect elderly and children.",
#             "🏥 Seek medical help if breathing issues.",
#         ]

# def best_outdoor_time(aqi):
#     if aqi <= 100:   return "🕕 Any time is fine. Morning (6–8 AM) is freshest."
#     elif aqi <= 200: return "🕔 Early morning (5–7 AM) before traffic peaks."
#     else:            return "🚫 Not recommended to go outside today."


# # =========================================
# # BUILD & SEND MESSAGE
# # =========================================
# def build_message():
#     now_ist = datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST")
#     lines = [
#         f"🌫️ *Daily AQI Morning Alert*",
#         f"📅 {now_ist}",
#         f"{'─' * 30}",
#     ]

#     for city in CITIES:
#         aqi, raw = fetch_aqi(city)
#         if aqi is None:
#             lines.append(f"\n📍 *{city}*: Data unavailable")
#             continue

#         cat_label, cat_emoji = category(aqi)
#         advice = get_advice(aqi)
#         outdoor = best_outdoor_time(aqi)

#         lines.append(f"\n📍 *{city}*")
#         lines.append(f"{cat_emoji} AQI: *{aqi}* — {cat_label}")
#         lines.append(f"")
#         lines.append(f"💡 *Advice:*")
#         for tip in advice:
#             lines.append(f"  {tip}")
#         lines.append(f"⏰ {outdoor}")

#         if raw:
#             pollutants = {k: v for k, v in raw.items() if v is not None}
#             if pollutants:
#                 worst_key = max(pollutants, key=lambda k: pollutants[k])
#                 lines.append(f"🔬 Highest pollutant: *{worst_key}* ({pollutants[worst_key]})")

#         lines.append(f"{'─' * 30}")

#     lines.append("\n_This alert is sent daily at 8:00 AM IST._")
#     return "\n".join(lines)


# def send_alert():
#     print(f"[{datetime.now(IST).strftime('%H:%M:%S')}] Sending daily AQI alert...")
#     msg = build_message()
#     url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
#     try:
#         res = requests.post(url, data={
#             "chat_id":    CHAT_ID,
#             "text":       msg,
#             "parse_mode": "Markdown",
#         }, timeout=15)
#         if res.status_code == 200:
#             print("✅ Alert sent successfully.")
#         else:
#             print(f"❌ Failed: {res.text}")
#     except Exception as e:
#         print(f"❌ Error sending alert: {e}")


# # =========================================
# # SCHEDULER — 8:00 AM IST daily
# # =========================================
# def run_scheduler():
#     # Schedule at 08:00 IST
#     # Render servers run UTC — IST = UTC+5:30 — so 08:00 IST = 02:30 UTC
#     schedule.every().day.at("02:30").do(send_alert)

#     print("🤖 Telegram AQI Bot started. Waiting for 8:00 AM IST...")
#     print(f"   Current time: {datetime.now(IST).strftime('%d %b %Y %I:%M %p IST')}")

#     # Send one immediately on startup for testing (comment out in production)
#     # send_alert()

#     while True:
#         schedule.run_pending()
#         time.sleep(30)


# if __name__ == "__main__":
#     run_scheduler()



import requests
import schedule
import time
from datetime import datetime
import pytz
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
AQICN_API = os.getenv("AQICN_API_KEY")

CITIES = ["Delhi", "Mumbai", "Bangalore"]

IST = pytz.timezone("Asia/Kolkata")


# --------------------------
# FETCH AQI
# --------------------------
def fetch_aqi(city):
    try:
        url = f"https://api.waqi.info/feed/{city}/?token={AQICN_API}"
        res = requests.get(url, timeout=10).json()

        if res["status"] != "ok":
            return None,None

        iaqi = res["data"]["iaqi"]

        raw = {
            "PM2.5": iaqi.get("pm25",{}).get("v"),
            "PM10": iaqi.get("pm10",{}).get("v"),
            "NO2": iaqi.get("no2",{}).get("v"),
            "SO2": iaqi.get("so2",{}).get("v"),
            "CO": iaqi.get("co",{}).get("v"),
            "O3": iaqi.get("o3",{}).get("v")
        }

        vals=[v for v in raw.values() if v is not None]

        if not vals:
            return None,None

        return int(max(vals)),raw

    except Exception as e:
        print(e)
        return None,None


# --------------------------
# HELPERS
# --------------------------
def category(aqi):
    if aqi<=50:
        return "Good","🟢"
    elif aqi<=100:
        return "Satisfactory","🟡"
    elif aqi<=200:
        return "Moderate","🟠"
    elif aqi<=300:
        return "Poor","🔴"
    else:
        return "Severe","⚫"


def get_advice(aqi):
    if aqi<=100:
        return "Outdoor activity okay."
    elif aqi<=200:
        return "Avoid jogging 8-10 AM."
    else:
        return "Stay indoors when possible."


# --------------------------
# BUILD MESSAGE
# --------------------------
def build_message():

    now=datetime.now(IST).strftime("%d %b %Y %I:%M %p IST")

    lines=[
        "🌫️ Daily AQI Morning Alert",
        now,
        "--------------------------"
    ]

    for city in CITIES:

        aqi,raw=fetch_aqi(city)

        if aqi is None:
            continue

        label,emoji=category(aqi)

        lines.append(
           f"\n{emoji} {city}\nAQI: {aqi}\nStatus: {label}\nAdvice: {get_advice(aqi)}"
        )

    return "\n".join(lines)



# --------------------------
# SEND TELEGRAM
# --------------------------
def send_alert():

    msg=build_message()

    url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:
        r=requests.post(
            url,
            data={
               "chat_id":CHAT_ID,
               "text":msg
            },
            timeout=15
        )

        print(r.text)

    except Exception as e:
        print(e)



# --------------------------
# DAILY 8 AM IST
# Render uses UTC
# 08:00 IST = 02:30 UTC
# --------------------------
def run_scheduler():

    schedule.every().day.at("04:00").do(send_alert)

    print("Scheduler started...")

    while True:
        schedule.run_pending()
        time.sleep(30)



# --------------------------
# HEALTH SERVER FOR RENDER
# solves NO OPEN PORTS
# --------------------------
class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(
            b"AQI Bot Running"
        )

    def log_message(self,*args):
        pass


def run_health_server():

    port=int(
       os.environ.get("PORT",8080)
    )

    print(f"Port {port}")

    server=HTTPServer(
      ("0.0.0.0",port),
      HealthHandler
    )

    server.serve_forever()



# --------------------------
# MAIN
# --------------------------
if __name__=="__main__":

    threading.Thread(
       target=run_scheduler,
       daemon=True
    ).start()

    run_health_server()