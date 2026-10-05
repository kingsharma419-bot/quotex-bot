import os
import random
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = "8818308648:AAFXbT_Qtdze1EJdYund2Q11GPgfPlGFgKM"
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}/"
RENDER_URL = "https://quotex-bot-svsk.onrender.com"

# OTC Assets aur Timeframes
VALID_ASSETS = ["EUR/CHF", "USD/JPY", "NZD/USD", "AUD/CAD", "EUR/USD", "GBP/USD"]
VALID_TIMEFRAMES = ["1M", "2M", "5M"]

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
    return "Interactive Signal Bot is running live!"

@app.route(f'/{TOKEN}', methods=['POST'])
def receive_update():
    json_data = request.get_json()
    
    if json_data:
        # 1. Agar user ne button click kiya hai (Callback Query)
        if 'callback_query' in json_data:
            callback = json_data['callback_query']
            chat_id = callback['message']['chat']['id']
            data = callback['data'] # Jaise 'sig_EUR/CHF'
            
            if data.startswith('sig_'):
                asset = data.split('_')[1]
                timeframe = random.choice(VALID_TIMEFRAMES)
                rsi, direction, strength = calculate_rsi_signal(asset, timeframe)
                
                report = (
                    f"🎯 *CUSTOM TRADE SIGNAL* 🎯\n"
                    f"-----------------------------------\n"
                    f"🌍 *Asset:* {asset} (OTC)\n"
                    f"⏳ *Timeframe:* {timeframe}\n"
                    f"📈 *Signal:* {direction}\n"
                    f"📉 *RSI:* {rsi} | *Strength:* {strength}\n"
                    f"-----------------------------------\n"
                    f"⚡ *Ekdam fresh entry lo!*"
                )
                requests.post(f"{TELEGRAM_URL}sendMessage", json={
                    "chat_id": chat_id, 
                    "text": report, 
                    "parse_mode": "Markdown"
                })
            return {"status": "ok"}

        # 2. Agar user ne normal message bheja hai
        if 'message' in json_data:
            message = json_data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '').strip()
            
            if text.startswith('/start') or text.startswith('/signal'):
                # Currency select karne ke liye Inline Keyboard buttons bana rahe hain
                keyboard = {
                    "inline_keyboard": [
                        [
                            {"text": "📊 EUR/CHF (OTC)", "callback_data": "sig_EUR/CHF"},
                            {"text": "📊 USD/JPY (OTC)", "callback_data": "sig_USD/JPY"}
                        ],
                        [
                            {"text": "📊 NZD/USD (OTC)", "callback_data": "sig_NZD/USD"},
                            {"text": "📊 AUD/CAD (OTC)", "callback_data": "sig_AUD/CAD"}
                        ],
                        [
                            {"text": "📊 EUR/USD (OTC)", "callback_data": "sig_EUR/USD"},
                            {"text": "📊 GBP/USD (OTC)", "callback_data": "sig_GBP/USD"}
                        ]
                    ]
                }
                
                welcome_msg = (
                    "⚡ *COMPOUND ALGO PRO (OTC)* ⚡\n"
                    "-----------------------------------\n"
                    "👋 *Swagat hai Dharmendra bhai!*\n"
                    "Neeche diye gaye buttons mein se apni pasand ki **Currency/Asset** select karo, aur turant live signal pao:"
                )
                requests.post(f"{TELEGRAM_URL}sendMessage", json={
                    "chat_id": chat_id, 
                    "text": welcome_msg, 
                    "parse_mode": "Markdown",
                    "reply_markup": keyboard
                })
                
    return {"status": "ok"}

def set_webhook():
    webhook_url = f"{RENDER_URL}/{TOKEN}"
    res = requests.get(f"{TELEGRAM_URL}setWebhook", params={"url": webhook_url})
    print("Webhook Setup Response:", res.json())

if __name__ == '__main__':
    set_webhook()
    app.run(host='0.0.0.0', port=8080)
