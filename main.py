import os
import json
import time
import threading
import requests
import telebot
from telebot import types
from flask import Flask

# 1. Web server for Render 24/7
app = Flask(__name__)

@app.route('/')
def home():
    return "OX NUMBER BOT IS RUNNING"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# 2. Configs
BOT_TOKEN = "8609353017:AAGN3B9DvcFBnUO809FyC3VfaslmeOyr_gI"
ADMIN_USER = "OxRehann"

CH1_ID = "@OxRehanCyber"
CH1_LINK = "https://t.me/OxRehanCyber"
CH2_LINK = "https://t.me/+852hkOgj0UNlZGU9"

API_BASE = "https://api-hub-alpha.vercel.app/api/number-info"
API_KEY = "cybershr1k_b800c6028c1935c39a"

DB_FILE = "caller_users.json"
user_states = {}

bot = telebot.TeleBot(BOT_TOKEN, skip_pending=True)

# Delete Webhook programmatically to prevent conflicts
try:
    bot.remove_webhook()
except:
    pass

# 3. Database
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"users": {}}

def save_db(data):
    try:
        with open(DB_FILE, 'w') as f:
            json.dump(data, f)
    except:
        pass

db = load_db()

def get_user(uid, username="User"):
    s = str(uid)
    if s not in db["users"]:
        db["users"][s] = {
            "name": username,
            "credits": 5,
            "invites": 0,
            "verified": False,
            "referrer": None
        }
        save_db(db)
    return db["users"][s]

def check_member(uid):
    try:
        st = bot.get_chat_member(CH1_ID, uid).status
        return st in ['member', 'administrator', 'creator']
    except Exception as e:
        # Agar bot channel me admin nahi hai toh error aane par block na kare
        return True

# 4. Keyboards
def verify_markup():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("📢 Join Channel 1", url=CH1_LINK),
        types.InlineKeyboardButton("📢 Join Channel 2", url=CH2_LINK),
        types.InlineKeyboardButton("⚡ VERIFY & UNLOCK ⚡", callback_data="chk_verify")
    )
    return kb

def main_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(types.KeyboardButton("🔍 Number To Info"))
    kb.add(types.KeyboardButton("💳 Balance"), types.KeyboardButton("🎁 Refer"))
    kb.add(types.KeyboardButton("💎 Buy Credits"), types.KeyboardButton("📢 Channel"))
    return kb

# 5. Handlers
@bot.message_handler(commands=['start'])
def start_handler(m):
    uid = m.from_user.id
    s = str(uid)
    args = m.text.split()
    user_name = m.from_user.first_name or "User"

    if s not in db["users"]:
        ref = args[1] if len(args) > 1 and args[1].isdigit() and args[1] != s else None
        db["users"][s] = {
            "name": user_name,
            "credits": 5,
            "invites": 0,
            "verified": False,
            "referrer": ref
        }
        save_db(db)

    u = db["users"][s]

    if not u.get("verified", False):
        bot.send_message(
            m.chat.id,
            f"👋 *Hey {user_name}!*\\n\\n"
            "⚠️ Bot ke saare features unlock karne ke liye official channels join karein.\\n\\n"
            "Join karne ke baad **⚡ VERIFY & UNLOCK ⚡** dabayein:",
            parse_mode='Markdown',
            reply_markup=verify_markup()
        )
        return

    bot.send_message(
        m.chat.id,
        f"👑 *WELCOME {user_name.upper()}*\\n\\n"
        f"👤 *Account:* `{uid}`\\n"
        f"💳 *Balance:* `{u['credits']} Credits`\\n"
        f"👥 *Invites:* `{u['invites']}`\\n\\n"
        "Neeche buttons se command choose karein 👇",
        parse_mode='Markdown',
        reply_markup=main_keyboard()
    )

@bot.callback_query_handler(func=lambda c: c.data == "chk_verify")
def verify_callback(c):
    uid = c.from_user.id
    u = get_user(uid, c.from_user.first_name)

    if check_member(uid):
        u["verified"] = True
        u["credits"] += 5

        ref_id = u.get("referrer")
        if ref_id and ref_id in db["users"]:
            db["users"][ref_id]["credits"] += 3
            db["users"][ref_id]["invites"] += 1
            u["referrer"] = None
            try:
                bot.send_message(
                    int(ref_id),
                    f"🎁 *Referral Bonus!*\\n\\n`{c.from_user.first_name}` joined using your link.\\n💎 *+3 Credits* added!",
                    parse_mode='Markdown'
                )
            except:
                pass

        save_db(db)
        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass

        bot.answer_callback_query(c.id, "✅ Verified successfully!")
        bot.send_message(
            c.message.chat.id,
            "🎉 *Account Verified!* Bot unlock ho gaya hai.",
            parse_mode='Markdown',
            reply_markup=main_keyboard()
        )
    else:
        bot.answer_callback_query(c.id, "❌ Pehle channels join karein!", show_alert=True)

# 6. Button Actions
@bot.message_handler(func=lambda m: "NUMBER TO INFO" in m.text.upper())
def num_info_click(m):
    u = get_user(m.from_user.id)
    if not u.get("verified", False):
        bot.send_message(m.chat.id, "🔒 Kripya pehle /start karke verify karein!", reply_markup=verify_markup())
        return

    if u["credits"] < 1:
        bot.send_message(
            m.chat.id,
            "⚠️ *Credits Khatam!*\\n\\nDetails nikalne ke liye minimum *1 Credit* chahiye. Refer karke credits badhayein.",
            parse_mode='Markdown',
            reply_markup=main_keyboard()
        )
        return

    user_states[m.from_user.id] = "waiting_for_number"
    bot.send_message(
        m.chat.id,
        "📱 *Enter 10-Digit Mobile Number:*\\n\\nJis number ki info nikalni hai wo type karke bhejein.\\n_(Cancel karne ke liye /cancel likhein)_",
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda m: "BALANCE" in m.text.upper())
def balance_click(m):
    user_states.pop(m.from_user.id, None)
    u = get_user(m.from_user.id, m.from_user.first_name)
    bot.send_message(
        m.chat.id,
        f"┌─── ❖ *ACCOUNT DETAILS* ❖ ───\\n"
        f"│ 👤 *User:* `{u['name']}`\\n"
        f"│ 🆔 *Account:* `{m.from_user.id}`\\n"
        f"│ 💳 *Balance:* `{u['credits']} Credits`\\n"
        f"│ 👥 *Invites:* `{u['invites']}`\\n"
        f"└─── ❖ ─────────────── ❖ ───",
        parse_mode='Markdown',
        reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda m: "REFER" in m.text.upper())
def refer_click(m):
    user_states.pop(m.from_user.id, None)
    uid = m.from_user.id
    bot_uname = bot.get_me().username
    bot.send_message(
        m.chat.id,
        f"🎁 *Referral Link (+3 Credits):*\\n"
        f"https://t.me/{bot_uname}?start={uid}\\n\\n"
        "Apne dosto ko share karein. Har join par 3 credits milenge!",
        reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda m: "BUY CREDITS" in m.text.upper())
def buy_click(m):
    user_states.pop(m.from_user.id, None)
    bot.send_message(
        m.chat.id,
        f"💎 *Credits khareedne ke liye admin se contact karein:*\\n👉 @{ADMIN_USER}",
        reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda m: "CHANNEL" in m.text.upper())
def channel_click(m):
    user_states.pop(m.from_user.id, None)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📢 Join Channel", url=CH1_LINK))
    bot.send_message(m.chat.id, "Hamara official channel join karein:", reply_markup=kb)

@bot.message_handler(commands=['cancel'])
def cancel_handler(m):
    user_states.pop(m.from_user.id, None)
    bot.send_message(m.chat.id, "❌ Cancel kar diya gaya.", reply_markup=main_keyboard())

# 7. Number Data Lookup
@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "waiting_for_number")
def process_number(m):
    uid = m.from_user.id
    user_states.pop(uid, None)
    u = get_user(uid, m.from_user.first_name)

    mobile = m.text.strip().replace(" ", "").replace("+91", "")
    if not mobile.isdigit() or len(mobile) != 10:
        bot.send_message(m.chat.id, "❌ Galat number! Kripya sahi 10-digit number bhejein.", reply_markup=main_keyboard())
        return

    load_msg = bot.send_message(m.chat.id, "🔍 *Searching Database...*", parse_mode='Markdown')

    try:
        req_url = f"{API_BASE}?key={API_KEY}&mobile={mobile}"
        r = requests.get(req_url, timeout=25)
        res = r.json()

        if not res or res.get("status") is False or res.get("success") is False:
            bot.edit_message_text("❌ Is number ka koi data nahi mila.", chat_id=m.chat.id, message_id=load_msg.message_id)
            return

        u["credits"] -= 1
        save_db(db)

        data = res.get("data", res)
        lines = [
            "╔══════════════════════════╗",
            "   🔍 *NUMBER INFORMATION*   ",
            "╚══════════════════════════╝\\n",
            f"📱 *Mobile:* `{mobile}`"
        ]

        if isinstance(data, dict):
            for k, v in data.items():
                if k.lower() not in ["status", "success", "key", "code"] and v:
                    lines.append(f"🔹 *{k.replace('_', ' ').title()}:* `{v}`")
        elif isinstance(data, list) and len(data) > 0:
            first = data[0]
            if isinstance(first, dict):
                for k, v in first.items():
                    if v:
                        lines.append(f"🔹 *{k.replace('_', ' ').title()}:* `{v}`")
        else:
            lines.append(f"🔹 *Result:* `{data}`")

        lines.append(f"\\n💳 *Remaining Credits:* `{u['credits']}`")

        bot.delete_message(m.chat.id, load_msg.message_id)
        bot.send_message(m.chat.id, "\\n".join(lines), parse_mode='Markdown', reply_markup=main_keyboard())

    except Exception as e:
        bot.edit_message_text("❌ API Server offline ya busy hai. Baad me try karein.", chat_id=m.chat.id, message_id=load_msg.message_id)

if __name__ == '__main__':
    threading.Thread(target=run_web, daemon=True).start()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
                    
