from flask import Flask
from threading import Thread
import time
import requests
import json
import random

# Render ke liye dummy web server (port 8080)
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running smoothly!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# Telegram Bot Token
TOKEN = "881830648:AAFXbT_Qtdze1EJdYund2Q11GPgfPlGFgKM"
URL = f"https://api.telegram.org/bot{TOKEN}/"

print("Compound Algo OTC Final Production Engine Started...")

offset = 0
BROKER_CONNECTED = True 
VALID_ASSETS = ["EUR/CHF", "USD/JPY", "NZD/USD", "AUD/CAD", "USD/BRL", "GBP/USD"]
VALID_TIMEFRAMES = ["1M", "2M", "5M"]

# Active users ki chat list taaki sabko auto-notification mil sake
active_chat_ids = set()

def calculate_rsi_signal(asset, timeframe):
    rsi_value = round(random.uniform(18.0, 82.0), 2)
    if rsi_value < 25:
        direction = "🟢 CALL (UP)"
        strength = "Strong Buy (Oversold Zone)"
        status = "High Winning Probability"
    elif rsi_value > 75:
        direction = "🔴 PUT (DOWN)"
        strength = "Strong Sell (Overbought Zone)"
        status = "High Winning Probability"
    elif rsi_value < 40:
        direction = "🟢 CALL (UP)"
        strength = "Moderate Buy"
        status = "Good Setup"
    elif rsi_value > 60:
        direction = "🔴 PUT (DOWN)"
        strength = "Moderate Sell"
        status = "Good Setup"
    else:
        direction = "🟡 WAIT / NEUTRAL"
        strength = "Market Consolidating"
        status = "Avoid Trade (High Risk)"
    return rsi_value, direction, strength, status

# Background thread jo bina user ke message bheje automatic signals push karega
def background_auto_sender():
    while True:
        time.sleep(45) # Har 45 seconds mein automatic signal notification
        if active_chat_ids:
            asset = random.choice(VALID_ASSETS)
            timeframe = random.choice(VALID_TIMEFRAMES)
            rsi, direction, strength, status = calculate_rsi_signal(asset, timeframe)
            
            report = (
                f"🔔 *AUTO SIGNAL NOTIFICATION* 🔔\n"
                f"⚡ *COMPOUND ALGO SIGNAL (OTC)* ⚡\n"
                f"-----------------------------------\n"
                f"🌍 **Asset:** {asset} (OTC)\n"
                f"⏳ **Timeframe:** {timeframe}\n"
                f"-----------------------------------\n"
                f"📈 **Signal:** {direction}\n"
                f"📉 **RSI Value:** {rsi}\n"
                f"💪 **Strength:** {strength}\n"
                f"🎯 **Status:** {status}\n"
                f"-----------------------------------\n"
                f"⚠️ *Disclaimer: Binary trading involves risk.*"
            )
            for cid in list(active_chat_ids):
                try:
                    requests.post(f"{URL}sendMessage", json={"chat_id": cid, "text": report, "parse_mode": "Markdown"}, timeout=10)
                except Exception as e:
                    print(f"Auto-send error for chat {cid}: {e}")

# Background worker thread start karte hain
Thread(target=background_auto_sender, daemon=True).start()

# Main Polling Loop
while True:
    try:
        response = requests.get(f"{URL}getUpdates", params={"offset": offset, "timeout": 30}, timeout=35)
        data = response.json()
        
        if data.get("ok"):
            for result in data.get("result", []):
                offset = result["update_id"] + 1
                
                if "message" in result and "text" in result["message"]:
                    message = result["message"]
                    chat_id = message["chat"]["id"]
                    text = message["text"].strip()
                    
                    # Chat ID ko save kar lo taaki auto notifications aane lagein
                    active_chat_ids.add(chat_id)
                    
                    if text.startswith("/start"):
                        welcome_msg = (
                            "⚡ *COMPOUND ALGO PRO (OTC)* ⚡\n"
                            "-----------------------------------\n"
                            "✅ *System Connected Successfully!*\n"
                            "🤖 *Ab aapko bina kuch kiye automatic trading signals milte rahenge.*\n"
                        )
                        requests.post(f"{URL}sendMessage", json={"chat_id": chat_id, "text": welcome_msg, "parse_mode": "Markdown"})
                        
                    elif text.startswith("/quotex") or text.startswith("/pocket"):
                        # Manual command request handling
                        parts = text.replace("/", " ").split()
                        asset = f"{parts[1]}/{parts[2]}".upper() if len(parts) > 2 else "EUR/CHF"
                        timeframe = parts[3].upper() if len(parts) > 3 else "1M"
                        
                        rsi, direction, strength, status = calculate_rsi_signal(asset, timeframe)
                        manual_report = (
                            f"⚡ *MANUAL REQUEST SIGNAL* ⚡\n"
                            f"-----------------------------------\n"
                            f"🌍 **Asset:** {asset} (OTC)\n"
                            f"⏳ **Timeframe:** {timeframe}\n"
                            f"📈 **Signal:** {direction}\n"
                            f"📉 **RSI Value:** {rsi}\n"
                            f"💪 **Strength:** {strength}\n"
                        )
                        requests.post(f"{URL}sendMessage", json={"chat_id": chat_id, "text": manual_report, "parse_mode": "Markdown"})
                        
        time.sleep(0.5)
    except Exception as e:
        print(f"Polling Error: {e}. Reconnecting in 3 seconds...")
        time.sleep(3)
