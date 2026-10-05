import os
import random
import requests
from flask import Flask, request

app = Flask(__name__)

# Tumhara bilkul sahi aur updated Telegram Bot Token
TOKEN = "8818308648:AAFXbT_Qtdze1EJdYund2Q11GPgfPlGFgKM"
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}/"
RENDER_URL = "https://quotex-bot-svsk.onrender.com"  # Tumhara Render URL

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
    return "Webhook Bot is running live!"

# Yeh route telegram se seedhe message receive karega
@app.route(f'/{TOKEN}', methods=['POST'])
def receive_update():
    json_data = request.get_json()
    if json_data and 'message' in json_data:
        message = json_data['message']
        chat_id = message['chat']['id']
        text = message.get('text', '').strip()
        
        active_chat_ids.add(chat_id)
        
        if text.startswith('/start'):
            welcome_msg = (
                "⚡ *COMPOUND ALGO PRO (OTC)* ⚡\n"
                "-----------------------------------\n"
                "✅ *Connected Successfully! Ab automatic signals milte rahenge.*\n"
            )
            requests.post(f"{TELEGRAM_URL}sendMessage", json={"chat_id": chat_id, "text": welcome_msg, "parse_mode": "Markdown"})
            
    return {"status": "ok"}

# Automatic set webhook function
def set_webhook():
    webhook_url = f"{RENDER_URL}/{TOKEN}"
    res = requests.get(f"{TELEGRAM_URL}setWebhook", params={"url": webhook_url})
    print("Webhook Setup Response:", res.json())

if __name__ == '__main__':
    set_webhook()
    app.run(host='0.0.0.0', port=8080)
