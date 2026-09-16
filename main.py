import os
import json
import time
import threading
import random
import string
import requests
import telebot
from telebot import types
from flask import Flask

# 1. 24/7 Web Server for Render
app = Flask(__name__)

@app.route('/')
def home():
    return "OX CALLER BOT RUNNING 24/7"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# 2. Configurations & Secret Admin Access
BOT_TOKEN = "8609353017:AAGN3B9DvcFBnUO809FyC3VfaslmeOyr_gI"
ADMIN_ID = 8671410379
ADMIN_USER = "OxRehann"

CH1_ID = "@OxRehanCyber"
CH1_LINK = "https://t.me/OxRehanCyber"
CH2_LINK = "https://t.me/+852hkOgj0UNlZGU9"

API_BASE = "https://api-hub-alpha.vercel.app/api/number-info"
API_KEY = "cybershr1k_b800c6028c1935c39a"

DB_FILE = "caller_users.json"
user_states = {}

bot = telebot.TeleBot(BOT_TOKEN, skip_pending=True)

try:
    bot.remove_webhook()
except Exception:
    pass

# 3. Permanent Database System
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                data = json.load(f)
                if "users" not in data:
                    data["users"] = {}
                if "redeems" not in data:
                    data["redeems"] = {}
                return data
        except Exception:
            pass
    return {"users": {}, "redeems": {}}

def save_db(data):
    try:
        with open(DB_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception:
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
    except Exception:
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

# 5. Secret Admin Features
@bot.message_handler(commands=['gen'])
def gen_code(m):
    if m.from_user.id != ADMIN_ID:
        return
    parts = m.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        bot.reply_to(m, "⚠️ Format: `/gen <credits>`\nExample: `/gen 10`", parse_mode='Markdown')
        return

    amt = int(parts[1])
    code = "OX-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    db["redeems"][code] = amt
    save_db(db)

    bot.reply_to(
        m,
        f"✅ <b>Redeem Code Created!</b>\n\n"
        f"🔑 <b>Code:</b> <code>{code}</code>\n"
        f"💎 <b>Value:</b> <code>{amt} Credits</code>\n\n"
        f"<i>Share this code with users:</i>\n<code>/claim {code}</code>",
        parse_mode='HTML'
    )

@bot.message_handler(commands=['all'])
def broadcast_all(m):
    if m.from_user.id != ADMIN_ID:
        return
    msg = m.text.replace("/all", "", 1).strip()
    if not msg:
        bot.reply_to(m, "⚠️ Message empty hai! Format: `/all Your message here`", parse_mode='Markdown')
        return

    users = list(db["users"].keys())
    sent = 0
    failed = 0
    stat_msg = bot.reply_to(m, f"🚀 Sending broadcast to {len(users)} users...")

    for u in users:
        try:
            bot.send_message(int(u), f"📢 <b>ANNOUNCEMENT:</b>\n\n{msg}", parse_mode='HTML')
            sent += 1
            time.sleep(0.05)
        except Exception:
            failed += 1

    bot.edit_message_text(
        f"✅ <b>Broadcast Completed!</b>\n\n📤 Sent: <code>{sent}</code>\n❌ Failed: <code>{failed}</code>",
        chat_id=m.chat.id,
        message_id=stat_msg.message_id,
        parse_mode='HTML'
    )

@bot.message_handler(commands=['add'])
def add_credits_cmd(m):
    if m.from_user.id != ADMIN_ID:
        return
    parts = m.text.split()
    if len(parts) < 3 or not parts[2].isdigit():
        bot.reply_to(m, "⚠️ Format: `/add <user_id> <amount>`\nExample: `/add 8671410379 20`", parse_mode='Markdown')
        return

    t_id = parts[1]
    amt = int(parts[2])
    target = get_user(t_id)
    target["credits"] += amt
    save_db(db)

    bot.reply_to(m, f"✅ <b>Success!</b> Added {amt} credits to <code>{t_id}</code>. Total: {target['credits']}", parse_mode='HTML')
    try:
        bot.send_message(int(t_id), f"💎 <b>Bonus Received!</b>\n\nAdmin credited <b>{amt} Credits</b> to your wallet!", parse_mode='HTML')
    except Exception:
        pass

@bot.message_handler(commands=['stats'])
def bot_stats(m):
    if m.from_user.id != ADMIN_ID:
        return
    t_users = len(db["users"])
    active_codes = len(db["redeems"])
    t_credits = sum(u.get("credits", 0) for u in db["users"].values())

    bot.reply_to(
        m,
        f"📊 <b>BOT LIVE STATS</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 <b>Total Users:</b> <code>{t_users}</code>\n"
        f"💳 <b>Circulating Credits:</b> <code>{t_credits}</code>\n"
        f"🎟️ <b>Active Codes:</b> <code>{active_codes}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━",
        parse_mode='HTML'
    )

# 6. User Redeem Claim Handler
@bot.message_handler(commands=['claim'])
def claim_code(m):
    uid = m.from_user.id
    parts = m.text.split()
    if len(parts) < 2:
        bot.reply_to(m, "⚠️ Format: <code>/claim YOUR-CODE</code>", parse_mode='HTML')
        return

    code = parts[1].strip()
    if code not in db["redeems"]:
        bot.reply_to(m, "❌ Invalid ya Expired Redeem Code!", parse_mode='HTML')
        return

    amt = db["redeems"].pop(code)
    u = get_user(uid, m.from_user.first_name)
    u["credits"] += amt
    save_db(db)

    bot.reply_to(
        m,
        f"🎉 <b>Code Redeemed Successfully!</b>\n\n"
        f"💎 Added: <b>+{amt} Credits</b>\n"
        f"💳 New Balance: <code>{u['credits']} Credits</code>",
        parse_mode='HTML',
        reply_markup=main_keyboard()
    )

# 7. Start & Force Join System
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
        welcome_join = (
            f"👋 <b>Hey, {user_name}!</b>\n\n"
            "⚠️ <b>Access Restricted!</b>\n"
            "Bot ke saare tools use karne ke liye pehle official channels join karein.\n\n"
            "Join karne ke baad niche <b>VERIFY & UNLOCK</b> dabayein 👇"
        )
        bot.send_message(m.chat.id, welcome_join, parse_mode='HTML', reply_markup=verify_markup())
        return

    welcome_msg = (
        f"👑 <b>WELCOME {user_name.upper()}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Account ID:</b> <code>{uid}</code>\n"
        f"💳 <b>Credits Balance:</b> <code>{u['credits']}</code>\n"
        f"👥 <b>Total Referrals:</b> <code>{u['invites']}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Niche diye gaye buttons se use karein 👇"
    )
    bot.send_message(m.chat.id, welcome_msg, parse_mode='HTML', reply_markup=main_keyboard())

@bot.callback_query_handler(func=lambda c: c.data == "chk_verify")
def verify_callback(c):
    uid = c.from_user.id
    u = get_user(uid, c.from_user.first_name)

    if check_member(uid):
        if not u.get("verified", False):
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
                        f"🎁 <b>Referral Bonus!</b>\n\n<code>{c.from_user.first_name}</code> ne aapka link use kiya.\n💎 <b>+3 Credits</b> add kar diye gaye!",
                        parse_mode='HTML'
                    )
                except Exception:
                    pass
            save_db(db)

        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except Exception:
            pass

        bot.answer_callback_query(c.id, "✅ Verified!")
        bot.send_message(
            c.message.chat.id,
            "🎉 <b>Account Verified Successfully!</b>\n\nBot unlock ho gaya hai. Ab aap features access kar sakte hain.",
            parse_mode='HTML',
            reply_markup=main_keyboard()
        )
    else:
        bot.answer_callback_query(c.id, "❌ Pehle dono channels join karein!", show_alert=True)

# 8. Button Events
@bot.message_handler(func=lambda m: "NUMBER TO INFO" in m.text.upper())
def num_info_click(m):
    u = get_user(m.from_user.id)
    if not u.get("verified", False):
        bot.send_message(m.chat.id, "🔒 Kripya pehle /start karke verify karein!", reply_markup=verify_markup())
        return

    if u["credits"] < 1:
        bot.send_message(
            m.chat.id,
            "⚠️ <b>Insufficient Credits!</b>\n\nSearch karne ke liye kam se kam <b>1 Credit</b> chahiye.\nRefer karke ya claim karke credits earn karein.",
            parse_mode='HTML',
            reply_markup=main_keyboard()
        )
        return

    user_states[m.from_user.id] = "waiting_for_number"
    bot.send_message(
        m.chat.id,
        "📱 <b>Enter 10-Digit Mobile Number:</b>\n\nJis number ka data nikalna hai wo type karke bhejein.\n<i>(Cancel karne ke liye /cancel likhein)</i>",
        parse_mode='HTML'
    )

@bot.message_handler(func=lambda m: "BALANCE" in m.text.upper())
def balance_click(m):
    user_states.pop(m.from_user.id, None)
    u = get_user(m.from_user.id, m.from_user.first_name)
    bal_card = (
        f"┌─── ❖ <b>ACCOUNT WALLET</b> ❖ ───\n"
        f"│ 👤 <b>User:</b> {u['name']}\n"
        f"│ 🆔 <b>Account ID:</b> <code>{m.from_user.id}</code>\n"
        f"│ 💳 <b>Balance:</b> <code>{u['credits']} Credits</code>\n"
        f"│ 👥 <b>Invites:</b> <code>{u['invites']}</code>\n"
        f"└─── ❖ ──────────────── ❖ ───"
    )
    bot.send_message(m.chat.id, bal_card, parse_mode='HTML', reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: "REFER" in m.text.upper())
def refer_click(m):
    user_states.pop(m.from_user.id, None)
    uid = m.from_user.id
    bot_uname = bot.get_me().username
    ref_card = (
        f"🎁 <b>REFERRAL PROGRAM</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔗 <b>Your Link:</b>\n"
        f"<code>https://t.me/{bot_uname}?start={uid}</code>\n\n"
        f"💎 Har friend ke verify karne par <b>3 Credits</b> milenge!\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    bot.send_message(m.chat.id, ref_card, parse_mode='HTML', reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: "BUY CREDITS" in m.text.upper())
def buy_click(m):
    user_states.pop(m.from_user.id, None)
    bot.send_message(
        m.chat.id,
        f"💎 <b>Recharge Credits:</b>\n\nCredits khareedne ke liye admin ko message karein:\n👉 @{ADMIN_USER}",
        parse_mode='HTML',
        reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda m: "CHANNEL" in m.text.upper())
def channel_click(m):
    user_states.pop(m.from_user.id, None)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📢 Join Channel", url=CH1_LINK))
    bot.send_message(m.chat.id, "Hamare updates channel ko join karein:", reply_markup=kb)

@bot.message_handler(commands=['cancel'])
def cancel_handler(m):
    user_states.pop(m.from_user.id, None)
    bot.send_message(m.chat.id, "❌ Action cancel kar diya gaya.", reply_markup=main_keyboard())

# 9. Number Lookup Execution
@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "waiting_for_number")
def process_number(m):
    uid = m.from_user.id
    user_states.pop(uid, None)
    u = get_user(uid, m.from_user.first_name)

    mobile = m.text.strip().replace(" ", "").replace("+91", "")
    if not mobile.isdigit() or len(mobile) != 10:
        bot.send_message(m.chat.id, "❌ <b>Invalid Number!</b> Kripya sahi 10-digit number enter karein.", parse_mode='HTML', reply_markup=main_keyboard())
        return

    load_msg = bot.send_message(m.chat.id, "🔍 <i>Searching database records...</i>", parse_mode='HTML')

    try:
        req_url = f"{API_BASE}?key={API_KEY}&mobile={mobile}"
        r = requests.get(req_url, timeout=25)
        res = r.json()

        if not res or res.get("status") is False or res.get("success") is False:
            bot.edit_message_text("❌ Is number ka koi record nahi mila.", chat_id=m.chat.id, message_id=load_msg.message_id)
            return

        u["credits"] -= 1
        save_db(db)

        records = []
        raw_data = res.get("data", res)

        if isinstance(raw_data, list):
            records = raw_data
        elif isinstance(raw_data, dict):
            if "data" in raw_data and isinstance(raw_data["data"], list):
                records = raw_data["data"]
            else:
                records = [raw_data]

        response_text = (
            f"╔══════════════════════════╗\n"
            f"   🔍 <b>NUMBER DETAILS FOUND</b>\n"
            f"╚══════════════════════════╝\n\n"
            f"📱 <b>Target Number:</b> <code>{mobile}</code>\n"
            f"📊 <b>Total Records:</b> <code>{len(records)}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
        )

        for i, rec in enumerate(records, 1):
            name = str(rec.get("name") or "N/A").strip()
            father = str(rec.get("father_name") or "N/A").strip()
            address = str(rec.get("address") or "N/A").strip().replace("\n", ", ")
            alt_phone = str(rec.get("alt_number") or "N/A").strip()
            circle = str(rec.get("circle") or "N/A").strip()

            response_text += (
                f"👤 <b>RECORD #{i}</b>\n"
                f"├ <b>Name:</b> {name}\n"
                f"├ <b>Father's Name:</b> {father}\n"
                f"├ <b>Alternate Mobile:</b> <code>{alt_phone}</code>\n"
                f"├ <b>Circle / Operator:</b> {circle}\n"
                f"└ <b>Address:</b> <i>{address}</i>\n\n"
            )

        response_text += (
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💳 <b>Remaining Credits:</b> <code>{u['credits']}</code>\n"
            f"<i>Powered by @{ADMIN_USER}</i>"
        )

        bot.delete_message(m.chat.id, load_msg.message_id)
        bot.send_message(m.chat.id, response_text, parse_mode='HTML', reply_markup=main_keyboard())

    except Exception:
        bot.edit_message_text("❌ Server busy ya data parse karne me problem aayi. Thodi der baad dubara try karein.", chat_id=m.chat.id, message_id=load_msg.message_id)

if __name__ == '__main__':
    threading.Thread(target=run_web, daemon=True).start()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
                     
