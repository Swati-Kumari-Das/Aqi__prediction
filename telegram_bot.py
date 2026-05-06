# # """
# # telegram_bot.py
# # ---------------
# # Runs as a SEPARATE background worker on Render.
# # Sends a daily AQI alert to Telegram at 8:00 AM IST every day.

# # Deploy as a "Background Worker" service on Render (not a Web Service).
# # Command: python telegram_bot.py
# # """

# # import requests
# # import schedule
# # import time
# # from datetime import datetime
# # import pytz
# # import os
# # from dotenv import load_dotenv


# # load_dotenv()

# # # =========================================
# # # CONFIG — replace with your values
# # # =========================================
# # BOT_TOKEN = os.getenv("BOT_TOKEN")
# # CHAT_ID = os.getenv("CHAT_ID")
# # AQICN_API = os.getenv("AQICN_API_KEY")
# # OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")

# # # Cities to monitor — add/remove as needed
# # CITIES = ["Delhi", "Mumbai", "Bangalore"]

# # IST = pytz.timezone("Asia/Kolkata")


# # # =========================================
# # # FETCH AQI
# # # =========================================
# # def fetch_aqi(city):
# #     try:
# #         url = f"https://api.waqi.info/feed/{city}/?token={AQICN_API}"
# #         res = requests.get(url, timeout=10).json()
# #         if res["status"] != "ok":
# #             return None, None
# #         iaqi = res["data"]["iaqi"]
# #         raw = {
# #             "PM2.5": iaqi.get("pm25", {}).get("v"),
# #             "PM10":  iaqi.get("pm10", {}).get("v"),
# #             "NO2":   iaqi.get("no2",  {}).get("v"),
# #             "SO2":   iaqi.get("so2",  {}).get("v"),
# #             "CO":    iaqi.get("co",   {}).get("v"),
# #             "O3":    iaqi.get("o3",   {}).get("v"),
# #         }
# #         vals = [v for v in raw.values() if v is not None]
# #         if not vals:
# #             return None, None
# #         return int(max(vals)), raw
# #     except Exception as e:
# #         print(f"[fetch_aqi] Error for {city}: {e}")
# #         return None, None


# # # =========================================
# # # AQI HELPERS
# # # =========================================
# # def category(aqi):
# #     if aqi <= 50:    return "Good ✅",         "🟢"
# #     elif aqi <= 100: return "Satisfactory 🙂",  "🟡"
# #     elif aqi <= 200: return "Moderate 😐",       "🟠"
# #     elif aqi <= 300: return "Poor 😷",           "🔴"
# #     elif aqi <= 400: return "Very Poor 🤢",      "🔴"
# #     else:            return "Severe ☠️",          "⚫"

# # def get_advice(aqi):
# #     if aqi <= 50:
# #         return [
# #             "✅ Air quality is good.",
# #             "🏃 Safe for all outdoor activities.",
# #             "💧 Stay hydrated.",
# #         ]
# #     elif aqi <= 100:
# #         return [
# #             "😷 Sensitive groups should wear a mask.",
# #             "🚶 Limit prolonged outdoor exposure.",
# #             "🪟 Keep windows closed during peak hours.",
# #         ]
# #     elif aqi <= 200:
# #         return [
# #             "😷 Wear N95 mask outdoors.",
# #             "🏃 Avoid jogging between 8–10 AM.",
# #             "🧴 Run air purifier indoors.",
# #         ]
# #     elif aqi <= 300:
# #         return [
# #             "🏠 Stay indoors as much as possible.",
# #             "😷 Wear N95/N99 mask if going out.",
# #             "🧴 Run purifier continuously.",
# #             "❌ Avoid all outdoor exercise.",
# #         ]
# #     else:
# #         return [
# #             "🚨 SEVERE: Stay strictly indoors.",
# #             "😷 Wear N99 mask even indoors.",
# #             "👨‍👩‍👧 Protect elderly and children.",
# #             "🏥 Seek medical help if breathing issues.",
# #         ]

# # def best_outdoor_time(aqi):
# #     if aqi <= 100:   return "🕕 Any time is fine. Morning (6–8 AM) is freshest."
# #     elif aqi <= 200: return "🕔 Early morning (5–7 AM) before traffic peaks."
# #     else:            return "🚫 Not recommended to go outside today."


# # # =========================================
# # # BUILD & SEND MESSAGE
# # # =========================================
# # def build_message():
# #     now_ist = datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST")
# #     lines = [
# #         f"🌫️ *Daily AQI Morning Alert*",
# #         f"📅 {now_ist}",
# #         f"{'─' * 30}",
# #     ]

# #     for city in CITIES:
# #         aqi, raw = fetch_aqi(city)
# #         if aqi is None:
# #             lines.append(f"\n📍 *{city}*: Data unavailable")
# #             continue

# #         cat_label, cat_emoji = category(aqi)
# #         advice = get_advice(aqi)
# #         outdoor = best_outdoor_time(aqi)

# #         lines.append(f"\n📍 *{city}*")
# #         lines.append(f"{cat_emoji} AQI: *{aqi}* — {cat_label}")
# #         lines.append(f"")
# #         lines.append(f"💡 *Advice:*")
# #         for tip in advice:
# #             lines.append(f"  {tip}")
# #         lines.append(f"⏰ {outdoor}")

# #         if raw:
# #             pollutants = {k: v for k, v in raw.items() if v is not None}
# #             if pollutants:
# #                 worst_key = max(pollutants, key=lambda k: pollutants[k])
# #                 lines.append(f"🔬 Highest pollutant: *{worst_key}* ({pollutants[worst_key]})")

# #         lines.append(f"{'─' * 30}")

# #     lines.append("\n_This alert is sent daily at 8:00 AM IST._")
# #     return "\n".join(lines)


# # def send_alert():
# #     print(f"[{datetime.now(IST).strftime('%H:%M:%S')}] Sending daily AQI alert...")
# #     msg = build_message()
# #     url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
# #     try:
# #         res = requests.post(url, data={
# #             "chat_id":    CHAT_ID,
# #             "text":       msg,
# #             "parse_mode": "Markdown",
# #         }, timeout=15)
# #         if res.status_code == 200:
# #             print("✅ Alert sent successfully.")
# #         else:
# #             print(f"❌ Failed: {res.text}")
# #     except Exception as e:
# #         print(f"❌ Error sending alert: {e}")


# # # =========================================
# # # SCHEDULER — 8:00 AM IST daily
# # # =========================================
# # def run_scheduler():
# #     # Schedule at 08:00 IST
# #     # Render servers run UTC — IST = UTC+5:30 — so 08:00 IST = 02:30 UTC
# #     schedule.every().day.at("02:30").do(send_alert)

# #     print("🤖 Telegram AQI Bot started. Waiting for 8:00 AM IST...")
# #     print(f"   Current time: {datetime.now(IST).strftime('%d %b %Y %I:%M %p IST')}")

# #     # Send one immediately on startup for testing (comment out in production)
# #     # send_alert()

# #     while True:
# #         schedule.run_pending()
# #         time.sleep(30)


# # if __name__ == "__main__":
# #     run_scheduler()


# ############################################################################################
# import requests
# import schedule
# import time
# from datetime import datetime
# import pytz
# import os
# import threading
# from http.server import HTTPServer, BaseHTTPRequestHandler
# from dotenv import load_dotenv

# load_dotenv()

# BOT_TOKEN = os.getenv("BOT_TOKEN")
# CHAT_ID = os.getenv("CHAT_ID")
# AQICN_API = os.getenv("AQICN_API_KEY")

# CITIES = ["Delhi", "Mumbai", "Bangalore"]

# IST = pytz.timezone("Asia/Kolkata")


# # --------------------------
# # FETCH AQI
# # --------------------------
# def fetch_aqi(city):
#     try:
#         url = f"https://api.waqi.info/feed/{city}/?token={AQICN_API}"
#         res = requests.get(url, timeout=10).json()

#         if res["status"] != "ok":
#             return None,None

#         iaqi = res["data"]["iaqi"]

#         raw = {
#             "PM2.5": iaqi.get("pm25",{}).get("v"),
#             "PM10": iaqi.get("pm10",{}).get("v"),
#             "NO2": iaqi.get("no2",{}).get("v"),
#             "SO2": iaqi.get("so2",{}).get("v"),
#             "CO": iaqi.get("co",{}).get("v"),
#             "O3": iaqi.get("o3",{}).get("v")
#         }

#         vals=[v for v in raw.values() if v is not None]

#         if not vals:
#             return None,None

#         return int(max(vals)),raw

#     except Exception as e:
#         print(e)
#         return None,None


# # --------------------------
# # HELPERS
# # --------------------------
# def category(aqi):
#     if aqi<=50:
#         return "Good","🟢"
#     elif aqi<=100:
#         return "Satisfactory","🟡"
#     elif aqi<=200:
#         return "Moderate","🟠"
#     elif aqi<=300:
#         return "Poor","🔴"
#     else:
#         return "Severe","⚫"


# def get_advice(aqi):
#     if aqi<=100:
#         return "Outdoor activity okay."
#     elif aqi<=200:
#         return "Avoid jogging 8-10 AM."
#     else:
#         return "Stay indoors when possible."


# # --------------------------
# # BUILD MESSAGE
# # --------------------------
# def build_message():

#     now=datetime.now(IST).strftime("%d %b %Y %I:%M %p IST")

#     lines=[
#         "🌫️ Daily AQI Morning Alert",
#         now,
#         "--------------------------"
#     ]

#     for city in CITIES:

#         aqi,raw=fetch_aqi(city)

#         if aqi is None:
#             continue

#         label,emoji=category(aqi)

#         lines.append(
#            f"\n{emoji} {city}\nAQI: {aqi}\nStatus: {label}\nAdvice: {get_advice(aqi)}"
#         )

#     return "\n".join(lines)



# # --------------------------
# # SEND TELEGRAM
# # --------------------------
# def send_alert():

#     msg=build_message()

#     url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

#     try:
#         r=requests.post(
#             url,
#             data={
#                "chat_id":CHAT_ID,
#                "text":msg
#             },
#             timeout=15
#         )

#         print(r.text)

#     except Exception as e:
#         print(e)



# # --------------------------
# # DAILY 8 AM IST
# # Render uses UTC
# # 08:00 IST = 02:30 UTC
# # --------------------------
# def run_scheduler():

#     schedule.every().day.at("16:45").do(send_alert)

#     print("Scheduler started...")

#     while True:
#         schedule.run_pending()
#         time.sleep(30)



# # --------------------------
# # HEALTH SERVER FOR RENDER
# # solves NO OPEN PORTS
# # --------------------------
# class HealthHandler(BaseHTTPRequestHandler):

#     def do_GET(self):
#         self.send_response(200)
#         self.end_headers()
#         self.wfile.write(
#             b"AQI Bot Running"
#         )

#     def log_message(self,*args):
#         pass


# def run_health_server():

#     port=int(
#        os.environ.get("PORT",8080)
#     )

#     print(f"Port {port}")

#     server=HTTPServer(
#       ("0.0.0.0",port),
#       HealthHandler
#     )

#     server.serve_forever()



# # --------------------------
# # MAIN
# # --------------------------
# if __name__=="__main__":

#     threading.Thread(
#        target=run_scheduler,
#        daemon=True
#     ).start()

#     run_health_server()
##############################################################################################

# import requests
# import schedule
# import time
# from datetime import datetime
# import pytz
# import os
# import threading
# from http.server import HTTPServer, BaseHTTPRequestHandler
# from dotenv import load_dotenv
# import json

# load_dotenv()

# BOT_TOKEN = os.getenv("BOT_TOKEN")
# AQICN_API = os.getenv("AQICN_API_KEY")

# SUB_FILE = "subscriptions.json"

# IST = pytz.timezone("Asia/Kolkata")


# # --------------------------
# # LOAD / SAVE USERS
# # --------------------------
# def load_users():
#     try:
#         with open(SUB_FILE, "r") as f:
#             return json.load(f)
#     except:
#         return {}

# def save_users(data):
#     with open(SUB_FILE, "w") as f:
#         json.dump(data, f, indent=4)


# def subscribe_user(chat_id, city):
#     users = load_users()
#     chat_id = str(chat_id)

#     if chat_id not in users:
#         users[chat_id] = []

#     if city not in users[chat_id]:
#         users[chat_id].append(city)

#     save_users(users)


# # --------------------------
# # FETCH AQI
# # --------------------------
# def fetch_aqi(city):
#     try:
#         url = f"https://api.waqi.info/feed/{city}/?token={AQICN_API}"
#         res = requests.get(url, timeout=10).json()

#         if res["status"] != "ok":
#             return None, None

#         iaqi = res["data"]["iaqi"]

#         raw = {
#             "PM2.5": iaqi.get("pm25", {}).get("v"),
#             "PM10": iaqi.get("pm10", {}).get("v"),
#             "NO2": iaqi.get("no2", {}).get("v"),
#             "SO2": iaqi.get("so2", {}).get("v"),
#             "CO": iaqi.get("co", {}).get("v"),
#             "O3": iaqi.get("o3", {}).get("v"),
#         }

#         vals = [v for v in raw.values() if v is not None]

#         if not vals:
#             return None, None

#         return int(max(vals)), raw

#     except Exception as e:
#         print(e)
#         return None, None


# # --------------------------
# # HELPERS
# # --------------------------
# def category(aqi):
#     if aqi <= 50:
#         return "Good", "🟢"
#     elif aqi <= 100:
#         return "Satisfactory", "🟡"
#     elif aqi <= 200:
#         return "Moderate", "🟠"
#     elif aqi <= 300:
#         return "Poor", "🔴"
#     else:
#         return "Severe", "⚫"


# def get_advice(aqi):
#     if aqi <= 100:
#         return "Outdoor activity okay."
#     elif aqi <= 200:
#         return "Avoid jogging 8-10 AM."
#     else:
#         return "Stay indoors when possible."


# # --------------------------
# # BUILD MESSAGE PER CITY
# # --------------------------
# def build_message(city, aqi):
#     label, emoji = category(aqi)

#     return (
#         f"🌫 AQI Alert\n"
#         f"{emoji} {city}\n"
#         f"AQI: {aqi}\n"
#         f"Status: {label}\n"
#         f"Advice: {get_advice(aqi)}"
#     )


# # --------------------------
# # SEND MESSAGE
# # --------------------------
# def send_message(chat_id, text):
#     url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

#     try:
#         requests.post(
#             url,
#             data={
#                 "chat_id": chat_id,
#                 "text": text,
#             },
#             timeout=10,
#         )
#     except Exception as e:
#         print(e)


# # --------------------------
# # SEND ALERT TO ALL USERS
# # --------------------------
# def send_alert_to_all():
#     users = load_users()

#     print("Sending alerts to users...")

#     for chat_id, cities in users.items():
#         for city in cities:
#             aqi, _ = fetch_aqi(city)

#             if aqi is None:
#                 continue

#             msg = build_message(city, aqi)
#             send_message(chat_id, msg)


# # --------------------------
# # HANDLE TELEGRAM COMMANDS
# # --------------------------
# def handle_updates():
#     last_update_id = None

#     while True:
#         url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
#         params = {"timeout": 30}

#         if last_update_id:
#             params["offset"] = last_update_id + 1

#         try:
#             res = requests.get(url, params=params).json()

#             for update in res.get("result", []):
#                 last_update_id = update["update_id"]

#                 message = update.get("message")
#                 if not message:
#                     continue

#                 chat_id = message["chat"]["id"]
#                 text = message.get("text", "")

#                 if text == "/start":
#                     send_message(chat_id, "👋 Welcome!\nUse /subscribe <city>")

#                 elif text.startswith("/subscribe"):
#                     parts = text.split()

#                     if len(parts) < 2:
#                         send_message(chat_id, "❌ Use: /subscribe delhi")
#                         continue

#                     city = parts[1].capitalize()
#                     subscribe_user(chat_id, city)

#                     send_message(chat_id, f"✅ Subscribed to {city}")

#         except Exception as e:
#             print("Update error:", e)

#         time.sleep(5)


# # --------------------------
# # SCHEDULER (8 AM IST)
# # --------------------------
# def run_scheduler():
#    # send_alert_to_all()
#     schedule.every().day.at("02:30").do(send_alert_to_all)

#     while True:
#         schedule.run_pending()
#         time.sleep(30)


# # --------------------------
# # HEALTH SERVER (RENDER FIX)
# # --------------------------
# class HealthHandler(BaseHTTPRequestHandler):
#     def do_GET(self):
#         self.send_response(200)
#         self.end_headers()
#         self.wfile.write(b"AQI Bot Running")

#     def log_message(self, *args):
#         pass


# def run_health_server():
#     port = int(os.environ.get("PORT", 8080))
#     server = HTTPServer(("0.0.0.0", port), HealthHandler)
#     server.serve_forever()


# # --------------------------
# # MAIN
# # --------------------------
# if __name__ == "__main__":
#     threading.Thread(target=run_scheduler, daemon=True).start()
#     threading.Thread(target=handle_updates, daemon=True).start()

#     run_health_server()


#######################################################################################################
"""
telegram_bot.py — Fixed version
"""

import requests
import schedule
import time
from datetime import datetime
import pytz
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv
import json

load_dotenv()

BOT_TOKEN       = os.getenv("BOT_TOKEN")
AQICN_API       = os.getenv("AQICN_API_KEY")
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")

SUB_FILE = "subscriptions.json"
IST      = pytz.timezone("Asia/Kolkata")


# =========================================
# COMMAND PARSER
# Handles /cmd, /cmd@botname, /CMD
# =========================================
def parse_command(text):
    """Returns (command_str, args_str) or (None, None). Command is lowercased, @botname stripped."""
    if not text or not text.startswith("/"):
        return None, None
    parts   = text[1:].split(None, 1)
    cmd_raw = parts[0].lower()
    if "@" in cmd_raw:
        cmd_raw = cmd_raw.split("@")[0]
    args = parts[1].strip() if len(parts) > 1 else ""
    return cmd_raw, args


# =========================================
# LOAD / SAVE SUBSCRIPTIONS
# Auto-migrates old list format to string
# =========================================
def load_users():
    try:
        with open(SUB_FILE, "r") as f:
            data = json.load(f)
        migrated = False
        for k, v in list(data.items()):
            if isinstance(v, list):
                data[k] = v[0] if v else ""
                migrated = True
        if migrated:
            save_users(data)
            print("[load_users] Migrated old list format.")
        return data
    except Exception:
        return {}


def save_users(data):
    with open(SUB_FILE, "w") as f:
        json.dump(data, f, indent=4)


def subscribe_user(chat_id, city):
    users = load_users()
    users[str(chat_id)] = city.strip().capitalize()
    save_users(users)


def unsubscribe_user(chat_id):
    users = load_users()
    key = str(chat_id)
    if key in users:
        del users[key]
        save_users(users)
        return True
    return False


def get_user_city(chat_id):
    return load_users().get(str(chat_id))


# =========================================
# FETCH AQI
# =========================================
def fetch_aqi(city):
    try:
        url = f"https://api.waqi.info/feed/{city}/?token={AQICN_API}"
        res = requests.get(url, timeout=10).json()
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
        return int(max(vals)), raw
    except Exception as e:
        print(f"[fetch_aqi] {city}: {e}")
        return None, None


# =========================================
# FETCH WEATHER
# =========================================
def fetch_weather(city):
    if not OPENWEATHER_KEY:
        return None
    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={OPENWEATHER_KEY}&units=metric"
        )
        res = requests.get(url, timeout=10).json()
        if str(res.get("cod")) != "200":
            return None
        return {
            "temp":      res["main"]["temp"],
            "humidity":  res["main"]["humidity"],
            "wind":      res["wind"]["speed"],
            "condition": res["weather"][0]["main"],
        }
    except Exception as e:
        print(f"[fetch_weather] {city}: {e}")
        return None


# =========================================
# BUILD RICH MESSAGE — plain text only
# (no Markdown/HTML to avoid send failures)
# =========================================
def build_rich_message(city_name, aqi_val, raw_data, weather_data, is_scheduled=False):
    now_ist = datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST")
    divider = "-" * 30

    if aqi_val <= 50:
        cat_label, cat_emoji = "Good",        "🟢"
    elif aqi_val <= 100:
        cat_label, cat_emoji = "Satisfactory","🟡"
    elif aqi_val <= 200:
        cat_label, cat_emoji = "Moderate",    "🟠"
    elif aqi_val <= 300:
        cat_label, cat_emoji = "Poor",        "🔴"
    elif aqi_val <= 400:
        cat_label, cat_emoji = "Very Poor",   "🔴"
    else:
        cat_label, cat_emoji = "Severe",      "⚫"

    if aqi_val <= 50:
        advice = ["Air is clean. Enjoy outdoor activities.", "Stay hydrated."]
    elif aqi_val <= 100:
        advice = ["Sensitive groups should wear a mask.", "Limit long outdoor stays."]
    elif aqi_val <= 200:
        advice = ["Wear N95 mask outdoors.", "Avoid jogging 8-10 AM.", "Use air purifier indoors."]
    elif aqi_val <= 300:
        advice = ["Stay indoors as much as possible.", "N95/N99 mask if going out.", "Avoid outdoor exercise."]
    else:
        advice = ["Stay strictly indoors.", "N99 mask even indoors.", "Seek help if breathing issues."]

    if aqi_val <= 100:
        outdoor_time = "Any time is fine. Morning (6-8 AM) is freshest."
    elif aqi_val <= 200:
        outdoor_time = "Early morning (5-7 AM) before traffic peaks."
    else:
        outdoor_time = "Not recommended to go outside today."

    pollutant_lines = ""
    if raw_data:
        for k, v in raw_data.items():
            if v is not None:
                pollutant_lines += f"  {k}: {v}\n"

    weather_lines = ""
    if weather_data:
        weather_lines = (
            f"\nWeather in {city_name}\n"
            f"  Temp     : {weather_data['temp']} C\n"
            f"  Humidity : {weather_data['humidity']}%\n"
            f"  Wind     : {weather_data['wind']} m/s\n"
            f"  Condition: {weather_data['condition']}\n"
        )

    footer = (
        "Daily alert sent at 8:00 AM IST."
        if is_scheduled
        else "You will now receive this alert daily at 8:00 AM IST."
    )

    lines = [
        f"AQI Alert - {city_name.upper()}",
        f"Date: {now_ist}",
        divider,
        "",
        f"{cat_emoji}  AQI: {aqi_val}  ({cat_label})",
        "",
        "Advice:",
    ]
    for tip in advice:
        lines.append(f"  - {tip}")
    lines += [
        "",
        f"Best time outdoors: {outdoor_time}",
        "",
        "Pollutants:",
        pollutant_lines.rstrip(),
    ]
    if weather_lines:
        lines.append(weather_lines.rstrip())
    lines += [divider, footer, "Powered by AQI Monitor App"]

    return "\n".join(lines)


# =========================================
# SEND MESSAGE — plain text, no parse_mode
# =========================================
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(
            url,
            json={"chat_id": chat_id, "text": text},
            timeout=15,
        )
        if r.status_code != 200:
            print(f"[send_message] Failed {chat_id}: {r.status_code} {r.text[:120]}")
        return r.status_code == 200
    except Exception as e:
        print(f"[send_message] Exception {chat_id}: {e}")
        return False


# =========================================
# SEND INSTANT ALERT
# =========================================
def send_instant_alert(chat_id, city):
    aqi, raw = fetch_aqi(city)
    if aqi is None:
        send_message(chat_id, f"Could not fetch AQI for '{city}'. Please check the city spelling and try again.")
        return
    weather = fetch_weather(city)
    msg     = build_rich_message(city, aqi, raw, weather, is_scheduled=False)
    send_message(chat_id, msg)


# =========================================
# SCHEDULED ALERT — all subscribers
# =========================================
def send_alert_to_all():
    users = load_users()
    now   = datetime.now(IST).strftime("%H:%M:%S IST")
    print(f"[{now}] Sending scheduled alerts to {len(users)} user(s)...")
    for chat_id, city in users.items():
        if not city or not isinstance(city, str):
            continue
        aqi, raw = fetch_aqi(city)
        if aqi is None:
            print(f"  SKIP - no AQI for {city} ({chat_id})")
            continue
        weather = fetch_weather(city)
        msg     = build_rich_message(city, aqi, raw, weather, is_scheduled=True)
        ok      = send_message(chat_id, msg)
        print(f"  {'OK' if ok else 'FAIL'} -> {chat_id} ({city})")


# =========================================
# TELEGRAM LONG POLLING
# =========================================
def handle_updates():
    last_update_id = None
    print("Bot started. Listening for messages...")

    while True:
        try:
            url    = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            params = {"timeout": 30}
            if last_update_id is not None:
                params["offset"] = last_update_id + 1

            res = requests.get(url, params=params, timeout=40).json()

            for update in res.get("result", []):

                # Advance offset FIRST — bad update can never cause infinite retry
                last_update_id = update["update_id"]

                try:
                    message = update.get("message")
                    if not message:
                        continue

                    chat_id    = message["chat"]["id"]
                    first_name = message["chat"].get("first_name", "there")
                    raw_text   = message.get("text", "").strip()

                    print(f"[{chat_id}] {first_name}: {raw_text!r}")

                    cmd, args = parse_command(raw_text)

                    if cmd is None:
                        continue   # Not a command — ignore

                    # /start
                    if cmd == "start":
                        send_message(
                            chat_id,
                            f"Hi {first_name}! Welcome to AQI Monitor Bot.\n\n"
                            "Commands:\n"
                            "  /subscribe <city>   - subscribe + get instant AQI\n"
                            "  /changecity <city>  - change your subscribed city\n"
                            "  /unsubscribe        - stop daily alerts\n"
                            "  /aqi                - get current AQI for your city\n\n"
                            "Example: /subscribe Delhi"
                        )

                    # /subscribe
                    elif cmd == "subscribe":
                        if not args:
                            send_message(chat_id, "Please provide a city name.\nExample: /subscribe Delhi")
                            continue
                        city_name = args.capitalize()
                        old_city  = get_user_city(chat_id)
                        subscribe_user(chat_id, city_name)
                        if old_city and old_city != city_name:
                            send_message(chat_id, f"City changed from {old_city} to {city_name}.\nFetching AQI now...")
                        else:
                            send_message(chat_id, f"Subscribed to {city_name}.\nFetching AQI now...")
                        send_instant_alert(chat_id, city_name)

                    # /changecity
                    elif cmd == "changecity":
                        if not args:
                            send_message(chat_id, "Please provide a city name.\nExample: /changecity Mumbai")
                            continue
                        city_name = args.capitalize()
                        old_city  = get_user_city(chat_id)
                        subscribe_user(chat_id, city_name)
                        send_message(chat_id, f"City updated from {old_city or 'none'} to {city_name}.\nFetching AQI now...")
                        send_instant_alert(chat_id, city_name)

                    # /unsubscribe
                    elif cmd == "unsubscribe":
                        removed = unsubscribe_user(chat_id)
                        if removed:
                            send_message(chat_id, "You have been unsubscribed from daily AQI alerts.\nSend /subscribe <city> to re-subscribe anytime.")
                        else:
                            send_message(chat_id, "You were not subscribed. Use /subscribe <city> to start.")

                    # /aqi
                    elif cmd == "aqi":
                        city_name = get_user_city(chat_id)
                        if not city_name:
                            send_message(chat_id, "You are not subscribed yet.\nUse /subscribe <city> first.")
                        else:
                            send_message(chat_id, f"Fetching current AQI for {city_name}...")
                            send_instant_alert(chat_id, city_name)

                    else:
                        send_message(
                            chat_id,
                            f"Unknown command: /{cmd}\n\n"
                            "Available commands:\n"
                            "  /subscribe <city>\n"
                            "  /changecity <city>\n"
                            "  /unsubscribe\n"
                            "  /aqi"
                        )

                except Exception as inner_e:
                    print(f"[handle_updates] Error on update {update.get('update_id')}: {inner_e}")

        except Exception as outer_e:
            print(f"[handle_updates] Request error: {outer_e}")
            time.sleep(5)

        time.sleep(1)


# =========================================
# SCHEDULER — 8:00 AM IST = 02:30 UTC
# =========================================
def run_scheduler():
    schedule.every().day.at("09:00").do(send_alert_to_all)
    now_ist = datetime.now(IST).strftime("%d %b %Y %I:%M %p IST")
    print(f"Scheduler ready. Daily alert at 8:00 AM IST. Now: {now_ist}")
    while True:
        schedule.run_pending()
        time.sleep(30)


# =========================================
# HEALTH SERVER (Render requirement)
# =========================================
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"AQI Bot Running")

    def log_message(self, *args):
        pass


def run_health_server():
    port   = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"Health server on port {port}")
    server.serve_forever()


# =========================================
# MAIN
# =========================================
if __name__ == "__main__":
    threading.Thread(target=run_scheduler,  daemon=True).start()
    threading.Thread(target=handle_updates, daemon=True).start()
    run_health_server()