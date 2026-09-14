import os
import re
import json
import threading
import requests
import telebot
from telebot import types
from flask import Flask

# Background Web Server (Render ke liye)
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
ADMIN_USERNAME = "OxRehann"
ADMIN_ID = 8671410379
CHANNEL_ID = -1003782903063

bot = telebot.TeleBot(BOT_TOKEN)
DB_FILE = "users_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

db = load_db()

def get_user(user_id):
    str_id = str(user_id)
    if str_id not in db:
        db[str_id] = {
            "credits": 5,
            "referred_by": None,
            "referrals": 0
        }
        save_db(db)
    return db[str_id]

def is_user_joined(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception:
        return True

def force_join_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_join = types.InlineKeyboardButton("📢 Join Channel", url=TG_CHANNEL_LINK)
    btn_verify = types.InlineKeyboardButton("🔄 Verify Membership", callback_data="verify_join")
    markup.add(btn_join, btn_verify)
    return markup

def main_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_profile = types.InlineKeyboardButton("💳 My Credits", callback_data="btn_profile")
    btn_refer = types.InlineKeyboardButton("🎁 Refer & Earn", callback_data="btn_refer")
    btn_buy = types.InlineKeyboardButton("💰 Buy Credits", callback_data="btn_buy")
    btn_contact = types.InlineKeyboardButton("💬 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}")
    markup.add(btn_profile, btn_refer)
    markup.add(btn_buy, btn_contact)
    return markup

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
    user_id = message.from_user.id
    str_id = str(user_id)
    args = message.text.split()

    if str_id not in db:
        referrer_id = None
        if len(args) > 1 and args[1].isdigit() and args[1] != str_id:
            referrer_id = args[1]
            if referrer_id in db:
                db[referrer_id]["credits"] += 3
                db[referrer_id]["referrals"] += 1
                try:
                    bot.send_message(int(referrer_id), f"🎉 *New Referral!*\nAapko *+3 Credits* mile hain!", parse_mode='Markdown')
                except Exception:
                    pass

        db[str_id] = {
            "credits": 5,
            "referred_by": referrer_id,
            "referrals": 0
        }
        save_db(db)

    if not is_user_joined(user_id):
        join_msg = (
            "⚠️ *Access Restricted!*\n\n"
            "Bot ko use karne ke liye pehle official channel join karein aur verify par click karein."
        )
        bot.reply_to(message, join_msg, parse_mode='Markdown', reply_markup=force_join_markup())
        return

    user_data = get_user(user_id)
    welcome_text = (
        f"👋 *Hello {message.from_user.first_name}!*\n\n"
        "⚡ *Welcome to Live Caller Info Bot*\n\n"
        f"💳 *Aapka Balance:* `{user_data['credits']} Credits`\n"
        "*(Har search par 1 credit use hoga)*\n\n"
        "🔍 Number details ke liye **10-digit mobile number** send karein.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👑 *Modded By Rehan*"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown', reply_markup=main_menu_markup())

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    if message.from_user.id != ADMIN_ID:
        return
    raw_text = message.text.replace('/broadcast', '').strip()
    if not raw_text:
        bot.reply_to(message, "Usage: `/broadcast Aapka message`", parse_mode='Markdown')
        return

    count = 0
    for uid in list(db.keys()):
        try:
            bot.send_message(int(uid), f"📢 *Announcement:*\n\n{raw_text}", parse_mode='Markdown')
            count += 1
        except Exception:
            pass
    bot.reply_to(message, f"✅ Broadcast sent to {count} users.")

@bot.message_handler(commands=['addcredit'])
def add_credits_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "Usage: `/addcredit <user_id> <amount>`", parse_mode='Markdown')
        return
    target_id, amount = parts[1], int(parts[2])
    if target_id in db:
        db[target_id]["credits"] += amount
        save_db(db)
        bot.reply_to(message, f"✅ Added {amount} credits to {target_id}.")
        try:
            bot.send_message(int(target_id), f"🎁 *Admin ne aapko {amount} credits diye hain!*", parse_mode='Markdown')
        except Exception:
            pass

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    user_data = get_user(user_id)

    if call.data == "verify_join":
        if is_user_joined(user_id):
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, "✅ *Channel verified successfully!* Ab 10-digit number send karein.", parse_mode='Markdown', reply_markup=main_menu_markup())
        else:
            bot.answer_callback_query(call.id, "❌ Aapne abhi tak channel join nahi kiya!", show_alert=True)

    elif call.data == "btn_profile":
        text = (
            f"👤 *Aapki Details:*\n\n"
            f"💳 *Available Credits:* `{user_data['credits']}`\n"
            f"👥 *Total Referrals:* `{user_data['referrals']}`\n"
            f"🆔 *User ID:* `{user_id}`"
        )
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, text, parse_mode='Markdown')

    elif call.data == "btn_refer":
        bot_info = bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
        text = (
            "🎁 *Refer & Earn System*\n\n"
            "Har valid refer par aapko **+3 Credits** milenge!\n\n"
            f"🔗 *Referral Link:*\n`{ref_link}`\n\n"
            f"👥 *Total Referrals:* `{user_data['referrals']}`"
        )
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, text, parse_mode='Markdown')

    elif call.data == "btn_buy":
        text = (
            "💰 *Buy Credits*\n\n"
            "Credits recharge karne ke liye Admin se direct baat karein:\n"
            f"👉 [@{ADMIN_USERNAME}](https://t.me/{ADMIN_USERNAME})"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💬 Buy via Admin", url=f"https://t.me/{ADMIN_USERNAME}"))
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def lookup_number(message):
    user_id = message.from_user.id

    if not is_user_joined(user_id):
        bot.reply_to(message, "⚠️ *Kripya pehle channel join karein!*", parse_mode='Markdown', reply_markup=force_join_markup())
        return

    user_data = get_user(user_id)

    if user_data["credits"] <= 0:
        bot_info = bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
        no_credit_msg = (
            "❌ *Aapka Credit Balance 0 Ho Chuka Hai!*\n\n"
            "Free credits ke liye refer karein (+3 per refer) ya admin se buy karein:\n\n"
            f"🔗 `{ref_link}`"
        )
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🎁 Refer Link", callback_data="btn_refer"),
            types.InlineKeyboardButton("💰 Buy Credits", url=f"https://t.me/{ADMIN_USERNAME}")
        )
        bot.reply_to(message, no_credit_msg, parse_mode='Markdown', reply_markup=markup)
        return

    text = message.text.strip()
    if not re.match(r'^[6-9]\d{9}$', text):
        bot.reply_to(message, "⚠️ *Kripya valid 10-digit Indian mobile number send karein.*", parse_mode='Markdown')
        return

    wait_msg = bot.reply_to(message, "🔍 *Searching database...*", parse_mode='Markdown')

    try:
        res = requests.get(API_URL, params={"key": API_KEY, "mobile": text}, timeout=12)
        data = res.json()

        name = find_deep_value(data, ['name', 'Name', 'fullName', 'caller', 'callerName', 'owner', 'user'])
        address = find_deep_value(data, ['address', 'Address', 'fullAddress', 'location_address', 'street', 'city'])
        carrier = find_deep_value(data, ['carrier', 'Carrier', 'operator', 'Operator', 'sim', 'network'])
        circle = find_deep_value(data, ['circle', 'Circle', 'telecom_circle', 'state', 'location', 'region'])
        alt_number = find_deep_value(data, ['alt_mobile', 'alt_phone', 'alternate_number', 'alt_num', 'alternatePhone'])

        if not name and not carrier and not circle and not address:
            err_msg = data.get('message') or "Details nahi mili."
            bot.edit_message_text(f"⚠️ *{err_msg}*", chat_id=message.chat.id, message_id=wait_msg.message_id, parse_mode='Markdown')
            return

        user_data["credits"] -= 1
        save_db(db)

        response_card = (
            "⚡ *LIVE CALLER INFORMATION* ⚡\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *Name:* `{name or 'Not Available'}`\n"
            f"📍 *Address:* `{address or 'Not Available'}`\n"
            f"📞 *Alt Number:* `{alt_number or 'Not Available'}`\n"
            f"📡 *Carrier:* `{carrier or 'Not Available'}`\n"
            f"🌐 *Circle:* `{circle or 'Not Available'}`\n"
            f"📱 *Searched Number:* `{text}`\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"💳 *Remaining Credits:* `{user_data['credits']}`\n"
            "👑 *Modded By Rehan* | All Rights Reserved"
        )
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📢 Channel", url=TG_CHANNEL_LINK),
            types.InlineKeyboardButton("💬 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}")
        )
        bot.edit_message_text(response_card, chat_id=message.chat.id, message_id=wait_msg.message_id, parse_mode='Markdown', reply_markup=markup)

    except Exception as e:
        bot.edit_message_text(f"❌ *Error:* `{str(e)}`", chat_id=message.chat.id, message_id=wait_msg.message_id, parse_mode='Markdown')

if __name__ == '__main__':
    threading.Thread(target=run_web).start()
    bot.infinity_polling()
        
