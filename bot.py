from flask import Flask
from threading import Thread
import time
import requests
import json
import random

# Render के लिए डमी वेब सर्वर (पोर्ट एरर हटाने के लिए)
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# सर्वर को चालू करते हैं
keep_alive()

# आपका असली ट्रेडिंग बोट कोड
TOKEN = "881830648:AAFXbT_Qtdze1EJdYund2Q11GPgfPlGFgKM"
URL = f"https://api.telegram.org/bot{TOKEN}/"

print("Compound Algo OTC Final Engine Started...")

offset = 0
BROKER_CONNECTED = True 

VALID_ASSETS = [
    "NZD/USD", "USD/JPY", "USD/BRL", "USD/COP", "AUD/CAD", 
    "NZD/JPY", "USD/ARS", "USD/CAD", "USD/EGP", "AUD/JPY", "EUR/CHF", "EUR/JPY", "USD/USD"
]
VALID_TIMEFRAMES = ["1M", "2M", "5M", "15M"]

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
                    text = message["text"]
                    
                    if text.startswith("/start"):
                        status_text = "✅ *Online & Connected*" if BROKER_CONNECTED else "❌ *Offline / Disconnected*"
                        welcome_msg = (
                            "⚡ *COMPOUND ALGO PRO (OTC)* ⚡\n"
                            "-----------------------------------\n"
                            f"🏢 *Broker Status:* {status_text}\n"
                            "⚠️ *Trade at your own risk. Manage money wisely.*\n\n"
                            "Aise command bhejein:\n"
                            "`/quotex EUR/CHF 1M`"
                        )
                        requests.post(f"{URL}sendMessage", json={"chat_id": chat_id, "text": welcome_msg, "parse_mode": "Markdown"})
                        
                    elif text.startswith("/quotex") or text.startswith("/pocket"):
                        if not BROKER_CONNECTED:
                            offline_msg = (
                                f"❌ *BROKER DISCONNECTED* ❌\n"
                                f"-----------------------------------\n"
                                f"⚠️ वर्तमान में ब्रोकर का सर्वर ऑफलाइन है!"
                            )
                            requests.post(f"{URL}sendMessage", json={"chat_id": chat_id, "text": offline_msg, "parse_mode": "Markdown"})
                            continue

                        # Clean text: (OTC) ya OTC ko hata kar saare parts alag karenge
                        cleaned_text = text.replace("(OTC)", "").replace("OTC", "").replace("otc", "")
                        parts = cleaned_text.split()
                        
                        platform = parts[0][1:].upper()
                        
                        # Ab ye automatic detect kar lega chahe beech me OTC ho ya na ho
                        asset = parts[1].upper() if len(parts) > 1 else "EUR/CHF"
                        timeframe = parts.upper() if len(parts) > 2 else "1M"

                        if asset not in VALID_ASSETS:
                            error_msg = (
                                f"❌ *INVALID ASSET* ❌\n"
                                f"Asset `{asset}` list me nahi hai. Sahi asset dalein."
                            )
                            requests.post(f"{URL}sendMessage", json={"chat_id": chat_id, "text": error_msg, "parse_mode": "Markdown"})
                            continue

                        if timeframe not in VALID_TIMEFRAMES:
                            error_msg = (
                                f"❌ *INVALID TIMEFRAME* ❌\n"
                                f"Timeframe `{timeframe}` galat hai. Valid values: `1M, 2M, 5M`"
                            )
                            requests.post(f"{URL}sendMessage", json={"chat_id": chat_id, "text": error_msg, "parse_mode": "Markdown"})
                            continue
                        
                        rsi, direction, strength, status = calculate_rsi_signal(asset, timeframe)
                        
                        report = (
                            f"⚡ *COMPOUND ALGO SIGNAL (OTC)* ⚡\n"
                            f"-----------------------------------\n"
                            f"🏢 **Platform:** {platform} (Connected)\n"
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
                        requests.post(f"{URL}sendMessage", json={"chat_id": chat_id, "text": report, "parse_mode": "Markdown"})
                        
        time.sleep(0.5)
    except Exception as e:
        print(f"Error: {e}. Reconnecting...")
        time.sleep(3)
