import os
import random
import requests
import time
from threading import Thread
from flask import Flask, request

app = Flask(__name__)

TOKEN = "8818308648:AAFXbT_Qtdze1EJdYund2Q11GPgfPlGFgKM"
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}/"
RENDER_URL = "https://quotex-bot-svsk.onrender.com"

VALID_ASSETS = ["EUR/CHF", "USD/JPY", "NZD/USD", "AUD/CAD"]
VALID_TIMEFRAMES = ["1M", "2M", "5M"]
active_chat_ids = set()

def calculate_rsi_signal(asset, timeframe):
    rsi_value = round(random.uniform(18.0, 82.0), 2)
    if rsi_value < 25:
        direction = "🟢 CALL (UP)"
        strength = "Strong Buy (Oversold)"
    elif rsi_value > 75:
        direction = "🔴 PUT (DOWN)"
        strength = "Strong Sell (Overbought)"
    elif rsi_value < 40:
        direction = "🟢 CALL (UP)"
        strength = "Moderate Buy"
    elif rsi_value > 60:
        direction = "🔴 PUT (DOWN)"
        strength = "Moderate Sell"
    else:
        direction = "🟡 WAIT / NEUTRAL"
        strength = "Consolidating"
    return rsi_value, direction, strength

@app.route('/')
def home():
    return "Webhook Bot with Auto-Signals is running live!"

@app.route(f'/{TOKEN}', methods=['POST'])
def receive_update():
    json_data = request.get_json()
    if json_data and 'message' in json_data:
        message = json_data['message']
        chat_id = message['chat']['id']
        text = message.get('text', '').strip()
        
        # Chat ID ko save kar lete hain taaki auto signal inhi par jaye
        active_chat_ids.add(chat_id)
        
        if text.startswith('/start'):
            welcome_msg = (
                "⚡ *COMPOUND ALGO PRO (OTC)* ⚡\n"
                "-----------------------------------\n"
                "✅ *Connected! Ab aapko har kuch der mein automatic signals milte rahenge.*\n"
            )
            requests.post(f"{TELEGRAM_URL}sendMessage", json={"chat_id": chat_id, "text": welcome_msg, "parse_mode": "Markdown"})
            
    return {"status": "ok"}

# Background Worker jo apne aap periodic signals bhejega
def background_signal_sender():
    while True:
        time.sleep(60) # Har 60 seconds (1 minute) mein signal bheージュga (ise apne hisab se badal sakte ho)
        if active_chat_ids:
            asset = random.choice(VALID_ASSETS)
            timeframe = random.choice(VALID_TIMEFRAMES)
            rsi, direction, strength = calculate_rsi_signal(asset, timeframe)
            
            report = (
                f"🔔 *AUTO SIGNAL NOTIFICATION* 🔔\n"
                f"-----------------------------------\n"
                f"🌍 **Asset:** {asset} (OTC)\n"
                f"⏳ **Timeframe:** {timeframe}\n"
                f"📈 **Signal:** {direction}\n"
                f"📉 **RSI:** {rsi} | **Strength:** {strength}\n"
                f"-----------------------------------\n"
            )
            for cid in list(active_chat_ids):
                try:
                    requests.post(f"{TELEGRAM_URL}sendMessage", json={"chat_id": cid, "text": report, "parse_mode": "Markdown"}, timeout=10)
                except:
                    pass

def set_webhook():
    webhook_url = f"{RENDER_URL}/{TOKEN}"
    res = requests.get(f"{TELEGRAM_URL}setWebhook", params={"url": webhook_url})
    print("Webhook Setup Response:", res.json())

if __name__ == '__main__':
    set_webhook()
    # Background thread start kar rahe hain
    Thread(target=background_signal_sender, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
