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
######################################################################################################
# """
# telegram_bot.py
# ---------------
# Runs as a background worker (e.g. on Render).
# Stores subscribers in a local subscriptions.json file.
# Sends a personalised daily AQI alert at 8:00 AM IST to every subscriber.

# Deploy command : python telegram_bot.py
# """

# import json
# import os
# import requests
# import schedule
# import threading
# import time
# from datetime import datetime
# from http.server import BaseHTTPRequestHandler, HTTPServer

# import pytz
# from dotenv import load_dotenv

# load_dotenv()

# # =========================================
# # CONFIG
# # =========================================
# BOT_TOKEN       = os.getenv("BOT_TOKEN")
# AQICN_API       = os.getenv("AQICN_API_KEY")
# OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")

# IST      = pytz.timezone("Asia/Kolkata")
# SUB_FILE = "subscriptions.json"   # lives next to this script

# # Prevents send_alert_to_all() from running twice simultaneously
# # (e.g. scheduler fires at the same moment as a /send-alerts HTTP hit)
# _alert_lock = threading.Lock()


# # =========================================
# # LOCAL FILE STORAGE
# # Format: { "chat_id_string": "CityName", ... }
# # =========================================
# def load_users() -> dict:
#     """
#     Load subscribers from subscriptions.json.
#     Returns an empty dict if the file does not exist yet.
#     """
#     if not os.path.exists(SUB_FILE):
#         print(f"[load_users] {SUB_FILE} not found — starting with empty subscriber list.")
#         return {}
#     try:
#         with open(SUB_FILE, "r", encoding="utf-8") as f:
#             data = json.load(f)
#         print(f"[load_users] Loaded {len(data)} subscriber(s) from {SUB_FILE}: {data}")
#         return data
#     except json.JSONDecodeError as e:
#         print(f"[load_users] JSON parse error in {SUB_FILE}: {e} — returning empty dict.")
#         return {}
#     except Exception as e:
#         print(f"[load_users] Unexpected error: {e} — returning empty dict.")
#         return {}


# def save_users(data: dict) -> None:
#     """
#     Persist the subscriber dict to subscriptions.json.
#     Creates the file if it does not exist.
#     """
#     try:
#         with open(SUB_FILE, "w", encoding="utf-8") as f:
#             json.dump(data, f, indent=4, ensure_ascii=False)
#         print(f"[save_users] Saved {len(data)} subscriber(s) to {SUB_FILE}: {data}")
#     except Exception as e:
#         print(f"[save_users] Failed to save {SUB_FILE}: {e}")


# # =========================================
# # SUBSCRIBER HELPERS
# # =========================================
# def subscribe_user(chat_id, city: str) -> None:
#     """Add or update a subscriber's city."""
#     users = load_users()
#     key   = str(chat_id)
#     old   = users.get(key)
#     # Use .title() so "new delhi" → "New Delhi", "noida" → "Noida"
#     # .capitalize() would give "New delhi" (wrong for multi-word cities)
#     users[key] = city.strip().title()
#     save_users(users)
#     if old:
#         print(f"[subscribe_user] {key}: city updated {old!r} → {users[key]!r}")
#     else:
#         print(f"[subscribe_user] {key}: new subscriber → {users[key]!r}")


# def unsubscribe_user(chat_id) -> bool:
#     """Remove a subscriber. Returns True if they were found."""
#     users = load_users()
#     key   = str(chat_id)
#     if key in users:
#         removed_city = users.pop(key)
#         save_users(users)
#         print(f"[unsubscribe_user] {key} ({removed_city!r}) removed.")
#         return True
#     print(f"[unsubscribe_user] {key} not found in subscribers.")
#     return False


# def get_user_city(chat_id) -> str | None:
#     """Return the subscribed city for a chat_id, or None."""
#     return load_users().get(str(chat_id))


# # =========================================
# # COMMAND PARSER
# # Handles /cmd, /cmd@botname, /CMD
# # =========================================
# def parse_command(text):
#     if not text or not text.startswith("/"):
#         return None, None
#     parts   = text[1:].split(None, 1)
#     cmd_raw = parts[0].lower()
#     if "@" in cmd_raw:
#         cmd_raw = cmd_raw.split("@")[0]
#     args = parts[1].strip() if len(parts) > 1 else ""
#     return cmd_raw, args


# # =========================================
# # FETCH AQI
# # =========================================
# def fetch_aqi(city: str):
#     """
#     Returns (aqi_int, raw_dict) or (None, None) on failure.
#     Tries the city name as-is first, then lowercase as a fallback,
#     because the AQICN API is case-sensitive for some city slugs
#     (e.g. 'Noida' may fail but 'noida' works).
#     """
#     def _try(city_slug):
#         url = f"https://api.waqi.info/feed/{city_slug}/?token={AQICN_API}"
#         res = requests.get(url, timeout=10).json()
#         if res["status"] != "ok":
#             return None, None
#         iaqi = res["data"]["iaqi"]
#         raw  = {
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

#     try:
#         aqi, raw = _try(city)
#         if aqi is not None:
#             print(f"[fetch_aqi] {city!r} → AQI {aqi}")
#             return aqi, raw
#         # Fallback: try lowercase (AQICN slugs are usually lowercase)
#         aqi, raw = _try(city.lower())
#         if aqi is not None:
#             print(f"[fetch_aqi] {city!r} (lowercase fallback) → AQI {aqi}")
#             return aqi, raw
#         print(f"[fetch_aqi] API returned no data for {city!r} (tried both casings).")
#         return None, None
#     except Exception as e:
#         print(f"[fetch_aqi] Exception for {city!r}: {e}")
#         return None, None


# # =========================================
# # FETCH WEATHER
# # =========================================
# def fetch_weather(city: str):
#     if not OPENWEATHER_KEY:
#         return None
#     try:
#         url = (
#             f"https://api.openweathermap.org/data/2.5/weather"
#             f"?q={city}&appid={OPENWEATHER_KEY}&units=metric"
#         )
#         res = requests.get(url, timeout=10).json()
#         if str(res.get("cod")) != "200":
#             print(f"[fetch_weather] Non-200 for {city!r}: {res.get('message')}")
#             return None
#         return {
#             "temp":      res["main"]["temp"],
#             "humidity":  res["main"]["humidity"],
#             "wind":      res["wind"]["speed"],
#             "condition": res["weather"][0]["main"],
#         }
#     except Exception as e:
#         print(f"[fetch_weather] Exception for {city!r}: {e}")
#         return None


# # =========================================
# # BUILD RICH MESSAGE
# # =========================================
# def build_rich_message(city_name, aqi_val, raw_data, weather_data, is_scheduled=False):
#     now_ist = datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST")
#     divider = "-" * 30

#     if aqi_val <= 50:    cat_label, cat_emoji = "Good",         "🟢"
#     elif aqi_val <= 100: cat_label, cat_emoji = "Satisfactory", "🟡"
#     elif aqi_val <= 200: cat_label, cat_emoji = "Moderate",     "🟠"
#     elif aqi_val <= 300: cat_label, cat_emoji = "Poor",         "🔴"
#     elif aqi_val <= 400: cat_label, cat_emoji = "Very Poor",    "🔴"
#     else:                cat_label, cat_emoji = "Severe",       "⚫"

#     if aqi_val <= 50:
#         advice = ["Air is clean. Enjoy outdoor activities.", "Stay hydrated."]
#     elif aqi_val <= 100:
#         advice = ["Sensitive groups should wear a mask.", "Limit long outdoor stays."]
#     elif aqi_val <= 200:
#         advice = ["Wear N95 mask outdoors.", "Avoid jogging 8-10 AM.", "Use air purifier indoors."]
#     elif aqi_val <= 300:
#         advice = ["Stay indoors as much as possible.", "N95/N99 mask if going out.", "Avoid outdoor exercise."]
#     else:
#         advice = ["Stay strictly indoors.", "N99 mask even indoors.", "Seek help if breathing issues."]

#     if aqi_val <= 100:   outdoor_time = "Any time is fine. Morning (6-8 AM) is freshest."
#     elif aqi_val <= 200: outdoor_time = "Early morning (5-7 AM) before traffic peaks."
#     else:                outdoor_time = "Not recommended to go outside today."

#     pollutant_lines = ""
#     if raw_data:
#         for k, v in raw_data.items():
#             if v is not None:
#                 pollutant_lines += f"  {k}: {v}\n"

#     weather_lines = ""
#     if weather_data:
#         weather_lines = (
#             f"\nWeather in {city_name}\n"
#             f"  Temp     : {weather_data['temp']} C\n"
#             f"  Humidity : {weather_data['humidity']}%\n"
#             f"  Wind     : {weather_data['wind']} m/s\n"
#             f"  Condition: {weather_data['condition']}\n"
#         )

#     footer = (
#         "Daily alert — sent at 8:00 AM IST."
#         if is_scheduled
#         else "You will now receive this alert daily at 8:00 AM IST."
#     )

#     lines = [
#         f"AQI Alert - {city_name.upper()}",
#         f"Date: {now_ist}",
#         divider, "",
#         f"{cat_emoji}  AQI: {aqi_val}  ({cat_label})",
#         "", "Advice:",
#     ]
#     for tip in advice:
#         lines.append(f"  - {tip}")
#     lines += [
#         "",
#         f"Best time outdoors: {outdoor_time}",
#         "", "Pollutants:",
#         pollutant_lines.rstrip(),
#     ]
#     if weather_lines:
#         lines.append(weather_lines.rstrip())
#     lines += [divider, footer, "Powered by AQI Monitor App"]
#     return "\n".join(lines)


# # =========================================
# # SEND MESSAGE
# # =========================================
# def send_message(chat_id, text: str) -> bool:
#     url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
#     try:
#         r = requests.post(
#             url,
#             json={"chat_id": chat_id, "text": text},
#             timeout=15,
#         )
#         if r.status_code != 200:
#             print(f"[send_message] Failed → {chat_id}: {r.status_code} {r.text[:120]}")
#         return r.status_code == 200
#     except Exception as e:
#         print(f"[send_message] Exception → {chat_id}: {e}")
#         return False


# # =========================================
# # SEND INSTANT ALERT  (on subscribe / /aqi)
# # =========================================
# def send_instant_alert(chat_id, city: str) -> None:
#     aqi, raw = fetch_aqi(city)
#     if aqi is None:
#         send_message(
#             chat_id,
#             f"Could not fetch AQI for '{city}'. Please check the city name and try again."
#         )
#         return
#     weather = fetch_weather(city)
#     msg     = build_rich_message(city, aqi, raw, weather, is_scheduled=False)
#     send_message(chat_id, msg)


# # =========================================
# # SCHEDULED ALERT — runs at 8:00 AM IST
# # =========================================
# def send_alert_to_all() -> None:
#     """
#     Reads subscriptions.json and sends each subscriber the AQI
#     for their own city. One failure never stops the others.
#     """
#     try:
#         now_ist = datetime.now(IST).strftime("%H:%M:%S IST")
#         print(f"\n[scheduler] Triggered at {now_ist}")

#         users = load_users()
#         print(f"[scheduler] {len(users)} subscriber(s) found: {users}")

#         if not users:
#             print("[scheduler] No subscribers — skipping.")
#             return

#         for chat_id, city in users.items():
#             if not city or not isinstance(city, str):
#                 print(f"[scheduler] SKIP {chat_id} — invalid city value: {city!r}")
#                 continue
#             try:
#                 print(f"[scheduler] Sending to {chat_id} ({city!r})...")
#                 aqi, raw = fetch_aqi(city)
#                 if aqi is None:
#                     print(f"[scheduler] SKIP {chat_id} — no AQI data for {city!r}")
#                     continue
#                 weather = fetch_weather(city)
#                 msg     = build_rich_message(city, aqi, raw, weather, is_scheduled=True)
#                 ok      = send_message(chat_id, msg)
#                 print(f"[scheduler] {'OK' if ok else 'FAIL'} → {chat_id} ({city!r})")
#             except Exception as user_err:
#                 # Never let one user's failure stop the rest
#                 print(f"[scheduler] ERROR for {chat_id} ({city!r}): {user_err}")

#         print(f"[scheduler] Done.\n")

#     except Exception as outer_err:
#         print(f"[scheduler] Outer error: {outer_err}")


# # =========================================
# # FLUSH PENDING UPDATES ON STARTUP
# # =========================================
# def flush_pending_updates() -> None:
#     url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
#     try:
#         res     = requests.get(url, params={"timeout": 0}, timeout=10).json()
#         updates = res.get("result", [])
#         if updates:
#             last_id = updates[-1]["update_id"]
#             requests.get(url, params={"offset": last_id + 1, "timeout": 0}, timeout=10)
#             print(f"[startup] Flushed {len(updates)} pending update(s). Starting fresh.")
#         else:
#             print("[startup] No pending updates. Starting clean.")
#     except Exception as e:
#         print(f"[startup] Could not flush updates: {e}")


# # =========================================
# # TELEGRAM LONG POLLING
# # =========================================
# def handle_updates() -> None:
#     flush_pending_updates()

#     last_update_id = None
#     print("[bot] Listening for messages...")

#     while True:
#         try:
#             url    = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
#             params = {"timeout": 30}
#             if last_update_id is not None:
#                 params["offset"] = last_update_id + 1

#             res = requests.get(url, params=params, timeout=40).json()

#             for update in res.get("result", []):
#                 last_update_id = update["update_id"]

#                 try:
#                     message = update.get("message")
#                     if not message:
#                         continue

#                     chat_id    = message["chat"]["id"]
#                     first_name = message["chat"].get("first_name", "there")
#                     raw_text   = message.get("text", "").strip()

#                     print(f"[{chat_id}] {first_name}: {raw_text!r}")

#                     cmd, args = parse_command(raw_text)
#                     if cmd is None:
#                         continue

#                     # ── /start ──────────────────────────────────────────────
#                     if cmd == "start":
#                         send_message(
#                             chat_id,
#                             f"Hi {first_name}! Welcome to AQI Monitor Bot.\n\n"
#                             "Commands:\n"
#                             "  /subscribe <city>   — subscribe + get instant AQI\n"
#                             "  /changecity <city>  — change your subscribed city\n"
#                             "  /unsubscribe        — stop daily alerts\n"
#                             "  /aqi                — get current AQI for your city\n\n"
#                             "Example: /subscribe Delhi"
#                         )

#                     # ── /subscribe <city> ────────────────────────────────────
#                     elif cmd == "subscribe":
#                         if not args:
#                             send_message(
#                                 chat_id,
#                                 "Please provide a city name.\nExample: /subscribe Delhi"
#                             )
#                             continue
#                         city_name = args.strip().title()
#                         old_city  = get_user_city(chat_id)
#                         subscribe_user(chat_id, city_name)          # saves immediately
#                         if old_city and old_city != city_name:
#                             send_message(
#                                 chat_id,
#                                 f"City changed from {old_city} to {city_name}.\n"
#                                 "Fetching AQI now..."
#                             )
#                         else:
#                             send_message(
#                                 chat_id,
#                                 f"Subscribed to {city_name}!\n"
#                                 "You will get daily alerts at 8:00 AM IST.\n"
#                                 "Fetching AQI now..."
#                             )
#                         send_instant_alert(chat_id, city_name)

#                     # ── /changecity <city> ───────────────────────────────────
#                     elif cmd == "changecity":
#                         if not args:
#                             send_message(
#                                 chat_id,
#                                 "Please provide a city name.\nExample: /changecity Mumbai"
#                             )
#                             continue
#                         city_name = args.strip().title()
#                         old_city  = get_user_city(chat_id)
#                         subscribe_user(chat_id, city_name)          # updates existing entry
#                         send_message(
#                             chat_id,
#                             f"City updated from {old_city or 'none'} to {city_name}.\n"
#                             "Fetching AQI now..."
#                         )
#                         send_instant_alert(chat_id, city_name)

#                     # ── /unsubscribe ─────────────────────────────────────────
#                     elif cmd == "unsubscribe":
#                         removed = unsubscribe_user(chat_id)
#                         if removed:
#                             send_message(
#                                 chat_id,
#                                 "You have been unsubscribed from daily AQI alerts.\n"
#                                 "Send /subscribe <city> to re-subscribe anytime."
#                             )
#                         else:
#                             send_message(
#                                 chat_id,
#                                 "You were not subscribed. Use /subscribe <city> to start."
#                             )

#                     # ── /aqi ─────────────────────────────────────────────────
#                     elif cmd == "aqi":
#                         city_name = get_user_city(chat_id)
#                         if not city_name:
#                             send_message(
#                                 chat_id,
#                                 "You are not subscribed yet.\nUse /subscribe <city> first."
#                             )
#                         else:
#                             send_message(chat_id, f"Fetching current AQI for {city_name}...")
#                             send_instant_alert(chat_id, city_name)

#                     # ── unknown ───────────────────────────────────────────────
#                     else:
#                         send_message(
#                             chat_id,
#                             f"Unknown command: /{cmd}\n\n"
#                             "Available commands:\n"
#                             "  /subscribe <city>\n"
#                             "  /changecity <city>\n"
#                             "  /unsubscribe\n"
#                             "  /aqi"
#                         )

#                 except Exception as inner_e:
#                     print(f"[handle_updates] Error on update {update.get('update_id')}: {inner_e}")

#         except Exception as outer_e:
#             print(f"[handle_updates] Request error: {outer_e}")
#             time.sleep(5)

#         time.sleep(1)


# # =========================================
# # SCHEDULER
# # Render servers run UTC.
# # 8:00 AM IST  =  02:30 UTC
# # =========================================
# def run_scheduler() -> None:
#     schedule.every().day.at("17:30").do(send_alert_to_all)

#     now_ist = datetime.now(IST).strftime("%d %b %Y %I:%M %p IST")
#     print(f"[scheduler] Ready. Current time: {now_ist}")
#     print("[scheduler] Daily alerts scheduled at 8:00 AM IST (02:30 UTC).")

#     while True:
#         try:
#             schedule.run_pending()
#         except Exception as e:
#             print(f"[scheduler] run_pending error: {e}")
#         time.sleep(30)


# # =========================================
# # HEALTH / MANUAL-TRIGGER HTTP SERVER
# # Required by Render to detect an open port.
# # cron-job.org can hit /send-alerts to force
# # an immediate scheduled send.
# # =========================================
# class HealthHandler(BaseHTTPRequestHandler):

#     def do_GET(self):
#         if self.path == "/send-alerts":
#             print("[health-server] Manual /send-alerts trigger received.")
#             threading.Thread(target=send_alert_to_all, daemon=True).start()
#             self.send_response(200)
#             self.end_headers()
#             self.wfile.write(b"Alerts triggered successfully")
#             return

#         self.send_response(200)
#         self.end_headers()
#         self.wfile.write(b"AQI Bot Running")

#     def log_message(self, *args):
#         pass   # suppress default Apache-style access logs


# def run_health_server() -> None:
#     port   = int(os.environ.get("PORT", 8080))
#     server = HTTPServer(("0.0.0.0", port), HealthHandler)
#     print(f"[health-server] Listening on port {port}.")
#     server.serve_forever()


# # =========================================
# # MAIN
# # =========================================
# if __name__ == "__main__":
#     print("=" * 50)
#     print("AQI Monitor Telegram Bot — starting up")
#     print("=" * 50)

#     # Pre-load users so the initial log shows who's already subscribed
#     load_users()

#     threading.Thread(target=run_scheduler,  daemon=True).start()
#     threading.Thread(target=handle_updates, daemon=True).start()
#     run_health_server()   # blocks main thread — keep last





########################################
"""
telegram_bot.py
---------------
Runs as a Render Web Service.
Stores subscribers in Supabase (free PostgreSQL) — survives restarts/redeploys.
Sends a personalised daily AQI alert at 8:00 AM IST to every subscriber.

SETUP:
1. Create a free project at https://supabase.com
2. In Supabase SQL Editor, run:
       CREATE TABLE subscribers (
           chat_id TEXT PRIMARY KEY,
           city    TEXT NOT NULL
       );
3. Add SUPABASE_URL and SUPABASE_KEY to your Render env vars (see below).

Render env vars needed:
    BOT_TOKEN         — Telegram bot token
    AQICN_API_KEY     — AQICN API key
    OPENWEATHER_KEY   — OpenWeatherMap API key
    SUPABASE_URL      — e.g. https://xxxx.supabase.co
    SUPABASE_KEY      — anon/public key from Supabase > Settings > API
    PORT              — set automatically by Render (default 8080)

cron-job.org setup (IMPORTANT — fixes the "every 10 min all day" bug):
    Job 1: Keep Render Awake  → https://your-app.onrender.com/
           Schedule: every 10 minutes  (this is fine — just a ping)

    Job 2: AlertForAQI        → https://your-app.onrender.com/send-alerts
           Schedule: ONCE per day at 02:30 UTC  (= 8:00 AM IST)
           In cron-job.org: set Hours=2, Minutes=30, Days/Months/Weekdays = *
"""

import os
import requests
import schedule
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytz
from dotenv import load_dotenv

load_dotenv()

# =========================================
# CONFIG
# =========================================
BOT_TOKEN       = os.getenv("BOT_TOKEN")
AQICN_API       = os.getenv("AQICN_API_KEY")
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")
SUPABASE_URL    = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY    = os.getenv("SUPABASE_KEY", "")

IST = pytz.timezone("Asia/Kolkata")

# =========================================
# SUPABASE HELPERS  (REST API — no extra lib)
# =========================================

def _sb_headers():
    return {
        "apikey":        SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type":  "application/json",
        "Prefer":        "return=representation",
    }


def load_users() -> dict:
    """Return {chat_id_str: city_str} from Supabase."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("[load_users] SUPABASE_URL / SUPABASE_KEY not set — returning empty dict.")
        return {}
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/subscribers?select=chat_id,city",
            headers=_sb_headers(),
            timeout=10,
        )
        if r.status_code != 200:
            print(f"[load_users] Supabase error {r.status_code}: {r.text[:200]}")
            return {}
        rows = r.json()
        result = {row["chat_id"]: row["city"] for row in rows}
        print(f"[load_users] {len(result)} subscriber(s): {result}")
        return result
    except Exception as e:
        print(f"[load_users] Exception: {e}")
        return {}


def save_user(chat_id, city: str) -> bool:
    """
    Upsert a single subscriber (insert or update).
    Uses Supabase upsert so it works for both new and existing users.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("[save_user] Supabase not configured.")
        return False
    try:
        headers = _sb_headers()
        headers["Prefer"] = "resolution=merge-duplicates,return=representation"
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/subscribers",
            headers=headers,
            json={"chat_id": str(chat_id), "city": city.strip().title()},
            timeout=10,
        )
        ok = r.status_code in (200, 201)
        if ok:
            print(f"[save_user] Upserted chat_id={chat_id} city={city!r}")
        else:
            print(f"[save_user] Failed {r.status_code}: {r.text[:200]}")
        return ok
    except Exception as e:
        print(f"[save_user] Exception: {e}")
        return False


def delete_user(chat_id) -> bool:
    """Remove a subscriber from Supabase. Returns True if row existed."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False
    try:
        r = requests.delete(
            f"{SUPABASE_URL}/rest/v1/subscribers?chat_id=eq.{chat_id}",
            headers=_sb_headers(),
            timeout=10,
        )
        ok = r.status_code in (200, 204)
        print(f"[delete_user] chat_id={chat_id} → {'removed' if ok else 'not found / error'}")
        return ok
    except Exception as e:
        print(f"[delete_user] Exception: {e}")
        return False


def get_user_city(chat_id) -> str | None:
    """Return subscribed city for chat_id, or None."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/subscribers?chat_id=eq.{chat_id}&select=city",
            headers=_sb_headers(),
            timeout=10,
        )
        rows = r.json()
        return rows[0]["city"] if rows else None
    except Exception as e:
        print(f"[get_user_city] Exception: {e}")
        return None


# =========================================
# COMMAND PARSER
# =========================================
def parse_command(text):
    if not text or not text.startswith("/"):
        return None, None
    parts   = text[1:].split(None, 1)
    cmd_raw = parts[0].lower()
    if "@" in cmd_raw:
        cmd_raw = cmd_raw.split("@")[0]
    args = parts[1].strip() if len(parts) > 1 else ""
    return cmd_raw, args


# =========================================
# FETCH AQI
# =========================================
def fetch_aqi(city: str):
    """Returns (aqi_int, raw_dict) or (None, None) on failure."""
    def _try(slug):
        url = f"https://api.waqi.info/feed/{slug}/?token={AQICN_API}"
        res = requests.get(url, timeout=10).json()
        if res["status"] != "ok":
            return None, None
        iaqi = res["data"]["iaqi"]
        raw  = {
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

    try:
        aqi, raw = _try(city)
        if aqi is not None:
            return aqi, raw
        aqi, raw = _try(city.lower())
        if aqi is not None:
            return aqi, raw
        print(f"[fetch_aqi] No data for {city!r}")
        return None, None
    except Exception as e:
        print(f"[fetch_aqi] Exception for {city!r}: {e}")
        return None, None


# =========================================
# FETCH WEATHER
# =========================================
def fetch_weather(city: str):
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
        print(f"[fetch_weather] Exception for {city!r}: {e}")
        return None


# =========================================
# BUILD MESSAGE
# =========================================
def build_message(city_name, aqi_val, raw_data, weather_data, is_scheduled=False):
    now_ist = datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST")
    divider = "-" * 30

    if aqi_val <= 50:    cat_label, cat_emoji = "Good",         "🟢"
    elif aqi_val <= 100: cat_label, cat_emoji = "Satisfactory", "🟡"
    elif aqi_val <= 200: cat_label, cat_emoji = "Moderate",     "🟠"
    elif aqi_val <= 300: cat_label, cat_emoji = "Poor",         "🔴"
    elif aqi_val <= 400: cat_label, cat_emoji = "Very Poor",    "🔴"
    else:                cat_label, cat_emoji = "Severe",       "⚫"

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

    if aqi_val <= 100:   outdoor_time = "Any time is fine. Morning (6-8 AM) is freshest."
    elif aqi_val <= 200: outdoor_time = "Early morning (5-7 AM) before traffic peaks."
    else:                outdoor_time = "Not recommended to go outside today."

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
        "Daily alert — sent at 8:00 AM IST."
        if is_scheduled
        else "You will now receive this alert daily at 8:00 AM IST."
    )

    lines = [
        f"AQI Alert - {city_name.upper()}",
        f"Date: {now_ist}",
        divider, "",
        f"{cat_emoji}  AQI: {aqi_val}  ({cat_label})",
        "", "Advice:",
    ]
    for tip in advice:
        lines.append(f"  - {tip}")
    lines += [
        "",
        f"Best time outdoors: {outdoor_time}",
        "", "Pollutants:",
        pollutant_lines.rstrip(),
    ]
    if weather_lines:
        lines.append(weather_lines.rstrip())
    lines += [divider, footer, "Powered by AQI Monitor App"]
    return "\n".join(lines)


# =========================================
# SEND MESSAGE
# =========================================
def send_message(chat_id, text: str) -> bool:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(
            url,
            json={"chat_id": chat_id, "text": text},
            timeout=15,
        )
        if r.status_code != 200:
            print(f"[send_message] Failed → {chat_id}: {r.status_code} {r.text[:120]}")
        return r.status_code == 200
    except Exception as e:
        print(f"[send_message] Exception → {chat_id}: {e}")
        return False


def send_instant_alert(chat_id, city: str) -> None:
    aqi, raw = fetch_aqi(city)
    if aqi is None:
        send_message(chat_id, f"Could not fetch AQI for '{city}'. Please check the city name.")
        return
    weather = fetch_weather(city)
    msg     = build_message(city, aqi, raw, weather, is_scheduled=False)
    send_message(chat_id, msg)


# =========================================
# SCHEDULED ALERT — fires once at 8 AM IST
# (02:30 UTC on Render)
# =========================================
def send_alert_to_all() -> None:
    now_ist = datetime.now(IST).strftime("%d %b %Y %I:%M %p IST")
    print(f"\n[scheduler] Triggered at {now_ist}")

    users = load_users()
    print(f"[scheduler] {len(users)} subscriber(s): {users}")

    if not users:
        print("[scheduler] No subscribers — skipping.")
        return

    for chat_id, city in users.items():
        if not city or not isinstance(city, str):
            print(f"[scheduler] SKIP {chat_id} — invalid city: {city!r}")
            continue
        try:
            print(f"[scheduler] Sending to {chat_id} ({city!r})...")
            aqi, raw = fetch_aqi(city)
            if aqi is None:
                print(f"[scheduler] SKIP {chat_id} — no AQI data for {city!r}")
                continue
            weather = fetch_weather(city)
            msg     = build_message(city, aqi, raw, weather, is_scheduled=True)
            ok      = send_message(chat_id, msg)
            print(f"[scheduler] {'OK' if ok else 'FAIL'} → {chat_id} ({city!r})")
        except Exception as e:
            print(f"[scheduler] ERROR for {chat_id} ({city!r}): {e}")

    print("[scheduler] Done.\n")


# =========================================
# FLUSH PENDING TELEGRAM UPDATES ON STARTUP
# =========================================
def flush_pending_updates() -> None:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        res     = requests.get(url, params={"timeout": 0}, timeout=10).json()
        updates = res.get("result", [])
        if updates:
            last_id = updates[-1]["update_id"]
            requests.get(url, params={"offset": last_id + 1, "timeout": 0}, timeout=10)
            print(f"[startup] Flushed {len(updates)} pending update(s).")
        else:
            print("[startup] No pending updates.")
    except Exception as e:
        print(f"[startup] Could not flush updates: {e}")


# =========================================
# TELEGRAM LONG POLLING
# =========================================
def handle_updates() -> None:
    flush_pending_updates()
    last_update_id = None
    print("[bot] Listening for messages...")

    while True:
        try:
            url    = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            params = {"timeout": 30}
            if last_update_id is not None:
                params["offset"] = last_update_id + 1

            res = requests.get(url, params=params, timeout=40).json()

            for update in res.get("result", []):
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
                        continue

                    # ── /start ──────────────────────────────────────────
                    if cmd == "start":
                        send_message(
                            chat_id,
                            f"Hi {first_name}! Welcome to AQI Monitor Bot.\n\n"
                            "Commands:\n"
                            "  /subscribe <city>   — subscribe + get instant AQI\n"
                            "  /changecity <city>  — change your subscribed city\n"
                            "  /unsubscribe        — stop daily alerts\n"
                            "  /aqi                — get current AQI for your city\n\n"
                            "Example: /subscribe Delhi"
                        )

                    # ── /subscribe <city> ────────────────────────────────
                    elif cmd == "subscribe":
                        if not args:
                            send_message(chat_id, "Please provide a city.\nExample: /subscribe Delhi")
                            continue
                        city_name = args.strip().title()
                        old_city  = get_user_city(chat_id)
                        ok        = save_user(chat_id, city_name)  # ← Supabase upsert

                        if not ok:
                            send_message(chat_id, "⚠️ Database error. Please try again.")
                            continue

                        if old_city and old_city != city_name:
                            send_message(
                                chat_id,
                                f"City updated: {old_city} → {city_name}\n"
                                "Fetching AQI now..."
                            )
                        else:
                            send_message(
                                chat_id,
                                f"✅ Subscribed to {city_name}!\n"
                                "You'll get daily alerts at 8:00 AM IST.\n"
                                "Fetching AQI now..."
                            )
                        send_instant_alert(chat_id, city_name)

                    # ── /changecity <city> ───────────────────────────────
                    elif cmd == "changecity":
                        if not args:
                            send_message(chat_id, "Please provide a city.\nExample: /changecity Mumbai")
                            continue
                        city_name = args.strip().title()
                        old_city  = get_user_city(chat_id)
                        ok        = save_user(chat_id, city_name)  # ← Supabase upsert

                        if not ok:
                            send_message(chat_id, "⚠️ Database error. Please try again.")
                            continue

                        send_message(
                            chat_id,
                            f"✅ City updated: {old_city or 'none'} → {city_name}\n"
                            "Fetching AQI now..."
                        )
                        send_instant_alert(chat_id, city_name)

                    # ── /unsubscribe ─────────────────────────────────────
                    elif cmd == "unsubscribe":
                        removed = delete_user(chat_id)
                        if removed:
                            send_message(
                                chat_id,
                                "✅ Unsubscribed from daily AQI alerts.\n"
                                "Send /subscribe <city> to re-subscribe anytime."
                            )
                        else:
                            send_message(
                                chat_id,
                                "You were not subscribed.\nUse /subscribe <city> to start."
                            )

                    # ── /aqi ─────────────────────────────────────────────
                    elif cmd == "aqi":
                        city_name = get_user_city(chat_id)
                        if not city_name:
                            send_message(chat_id, "You are not subscribed yet.\nUse /subscribe <city> first.")
                        else:
                            send_message(chat_id, f"Fetching current AQI for {city_name}...")
                            send_instant_alert(chat_id, city_name)

                    # ── unknown ───────────────────────────────────────────
                    else:
                        send_message(
                            chat_id,
                            f"Unknown command: /{cmd}\n\n"
                            "Available:\n"
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
# SCHEDULER
# Runs internally at 02:30 UTC = 8:00 AM IST
# cron-job.org also hits /send-alerts at the
# same time as a reliable external trigger.
# =========================================
def run_scheduler() -> None:
    # 02:30 UTC = 08:00 IST
    schedule.every().day.at("02:30").do(send_alert_to_all)
    now_ist = datetime.now(IST).strftime("%d %b %Y %I:%M %p IST")
    print(f"[scheduler] Ready. Current IST time: {now_ist}")
    print("[scheduler] Daily alerts scheduled at 02:30 UTC (8:00 AM IST).")
    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            print(f"[scheduler] run_pending error: {e}")
        time.sleep(30)


# =========================================
# HEALTH / MANUAL-TRIGGER HTTP SERVER
# GET /           → health check (keep-alive ping)
# GET /send-alerts → manual trigger (called by cron-job.org once a day)
# =========================================
class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/send-alerts":
            print("[health-server] /send-alerts triggered externally.")
            # Run in background so HTTP response returns immediately
            threading.Thread(target=send_alert_to_all, daemon=True).start()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Alerts triggered successfully")
            return

        # Default: health check
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"AQI Bot Running")

    def log_message(self, *args):
        pass  # suppress access logs


def run_health_server() -> None:
    port   = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"[health-server] Listening on port {port}.")
    server.serve_forever()


# =========================================
# MAIN
# =========================================
if __name__ == "__main__":
    print("=" * 50)
    print("AQI Monitor Telegram Bot — starting up")
    print("=" * 50)

    # Verify Supabase config on startup
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("⚠️  WARNING: SUPABASE_URL or SUPABASE_KEY not set — subscriptions will NOT persist!")
    else:
        print(f"[startup] Supabase connected: {SUPABASE_URL}")
        load_users()  # log current subscribers

    threading.Thread(target=run_scheduler,  daemon=True).start()
    threading.Thread(target=handle_updates, daemon=True).start()
    run_health_server()  # blocks main thread — keep last
    #cha nged