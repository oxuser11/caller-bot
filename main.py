import os
import re
import threading
import requests
import telebot
from telebot import types
from flask import Flask

# Background web server (Render health-check ke liye)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running 24/7 by Rehan!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# Configurations
BOT_TOKEN = "8900604597:AAGN6rmhnOHkoPiJsrwPzUezcxVveDcLgN0"
API_KEY = "cybershr1k_6772fb6a04705e3268"
API_URL = "https://api-hub-alpha.vercel.app/api/number-info"
TG_CHANNEL_LINK = "https://t.me/+852hkOgj0UNlZGU9"

bot = telebot.TeleBot(BOT_TOKEN)

def find_deep_value(obj, keys):
    if not isinstance(obj, dict):
        return None
    for k in keys:
        if k in obj and obj[k] not in [None, "", "null"]:
            return obj[k]
    for k, v in obj.items():
        if isinstance(v, dict):
            res = find_deep_value(v, keys)
            if res:
                return res
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    res = find_deep_value(item, keys)
                    if res:
                        return res
    return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_first = message.from_user.first_name
    welcome_text = (
        f"👋 *Hello {user_first}!*\n\n"
        "⚡ *Welcome to Live Caller Info Bot*\n\n"
        "Kisi bhi number ki details janne ke liye **10-digit mobile number** send karein.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👑 *Modded By Rehan*"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 Join Telegram Channel", url=TG_CHANNEL_LINK))
    bot.reply_to(message, welcome_text, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def lookup_number(message):
    text = message.text.strip()
    if not re.match(r'^[6-9]\d{9}$', text):
        bot.reply_to(message, "⚠️ *Kripya valid 10-digit Indian mobile number enter karein.*", parse_mode='Markdown')
        return

    wait_msg = bot.reply_to(message, "🔍 *Searching database...*", parse_mode='Markdown')

    try:
        res = requests.get(API_URL, params={"key": API_KEY, "mobile": text}, timeout=12)
        data = res.json()

        name = find_deep_value(data, ['name', 'Name', 'fullName', 'caller', 'callerName', 'owner', 'user'])
        address = find_deep_value(data, ['address', 'Address', 'fullAddress', 'location_address', 'street', 'city'])
        carrier = find_deep_value(data, ['carrier', 'Carrier', 'operator', 'Operator', 'sim', 'network'])
        circle = find_deep_value(data, ['circle', 'Circle', 'telecom_circle', 'state', 'location', 'region'])

        if not name and not carrier and not circle and not address:
            err_msg = data.get('message') or "Details nahi mili."
            bot.edit_message_text(f"⚠️ *{err_msg}*", chat_id=message.chat.id, message_id=wait_msg.message_id, parse_mode='Markdown')
            return

        response_card = (
            "⚡ *LIVE CALLER INFORMATION* ⚡\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *Name:* `{name or 'Not Available'}`\n"
            f"📍 *Address:* `{address or 'Not Available'}`\n"
            f"📡 *Carrier:* `{carrier or 'Not Available'}`\n"
            f"🌐 *Circle:* `{circle or 'Not Available'}`\n"
            f"📱 *Number:* `{text}`\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "👑 *Modded By Rehan* | All Rights Reserved"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Join Channel", url=TG_CHANNEL_LINK))
        bot.edit_message_text(response_card, chat_id=message.chat.id, message_id=wait_msg.message_id, parse_mode='Markdown', reply_markup=markup)

    except Exception as e:
        bot.edit_message_text(f"❌ *Error:* `{str(e)}`", chat_id=message.chat.id, message_id=wait_msg.message_id, parse_mode='Markdown')

if __name__ == '__main__':
    threading.Thread(target=run_web).start()
    bot.infinity_polling()
      
