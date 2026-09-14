import os, re, json, random, string, threading, requests, telebot
from telebot import types
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "OX BOT 24/7 LIVE"

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

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
            with open(DB_FILE, 'r') as f: return json.load(f)
        except: return {}
    return {}

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f)

db = load_db()

def get_user(uid):
    s = str(uid)
    if s not in db:
        db[s] = {"credits": 5, "referrals": 0}
        save_db(db)
    return db[s]

def is_joined(uid):
    try:
        m = bot.get_chat_member(CHANNEL_ID, uid)
        return m.status in ['member', 'administrator', 'creator']
    except: return False

def find_deep(obj, keys):
    if not isinstance(obj, (dict, list)): return None
    if isinstance(obj, dict):
        for k in keys:
            if k in obj and obj[k] not in [None, "", "null", "None"]:
                return obj[k]
        for v in obj.values():
            res = find_deep(v, keys)
            if res: return res
    elif isinstance(obj, list):
        for item in obj:
            res = find_deep(item, keys)
            if res: return res
    return None

def permanent_kb():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    b1 = types.KeyboardButton("💳 Balance")
    b2 = types.KeyboardButton("🎁 Refer")
    b3 = types.KeyboardButton("💎 Buy Credits")
    b4 = types.KeyboardButton("📢 Channel")
    markup.add(b1, b2)
    markup.add(b3, b4)
    return markup

def join_kb():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("📢 Join Channel", url=TG_CHANNEL_LINK),
        types.InlineKeyboardButton("⚡ Verify Membership", callback_data="verify")
    )
    return kb

@bot.message_handler(commands=['start'])
def start_cmd(m):
    uid, text = m.from_user.id, m.text.split()
    s = str(uid)
    if s not in db:
        ref = text[1] if len(text) > 1 and text[1].isdigit() and text[1] != s else None
        if ref and ref in db:
            db[ref]["credits"] += 3
            db[ref]["referrals"] += 1
            try: bot.send_message(int(ref), "🎉 *Referral!* +3 Credits mil gaye!", parse_mode='Markdown')
            except: pass
        db[s] = {"credits": 5, "referrals": 0}
        save_db(db)
    
    if not is_joined(uid):
        bot.reply_to(m, "🔒 *Access Locked!*\nPehle hamara channel join karein aur verify dabayein.", parse_mode='Markdown', reply_markup=join_kb())
        return

    u = get_user(uid)
    msg = (
        f"⚡ *OX CALLER SYSTEM* ⚡\n\n"
        f"👋 Welcome, *{m.from_user.first_name}*!\n"
        f"💳 *Balance:* `{u['credits']} Credits`\n"
        f"👥 *Invites:* `{u['referrals']}`\n\n"
        f"🔍 *Search Number:* `/num 9876543210`\n"
        f"🎟 *Claim Voucher:* `/claim CODE`\n\n"
        f"👑 *Modded By Rehan* | `@{ADMIN_USERNAME}`"
    )
    bot.reply_to(m, msg, parse_mode='Markdown', reply_markup=permanent_kb())

@bot.message_handler(func=lambda m: m.text == "💳 Balance")
def btn_balance(m):
    uid = m.from_user.id
    u = get_user(uid)
    bot.reply_to(m, f"👤 *Account:* `{uid}`\n💳 *Balance:* `{u['credits']} Credits`\n👥 *Invites:* `{u['referrals']}`", parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "🎁 Refer")
def btn_refer(m):
    uid = m.from_user.id
    bot_info = bot.get_me()
    bot.reply_to(m, f"🎁 *Referral Link (+3 Credits):*\n`https://t.me/{bot_info.username}?start={uid}`", parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "💎 Buy Credits")
def btn_buy(m):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💬 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}"))
    bot.reply_to(m, f"💎 Credits buy karne ke liye Admin se contact karein:\n👉 `@{ADMIN_USERNAME}`", parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📢 Channel")
def btn_channel(m):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 Join Channel", url=TG_CHANNEL_LINK))
    bot.reply_to(m, "Official channel join karein naye updates ke liye:", reply_markup=markup)

@bot.message_handler(commands=['redeem'])
def gen_code(m):
    if m.from_user.id != ADMIN_ID: return
    p = m.text.split()
    if len(p) != 3:
        bot.reply_to(m, "⚠️ Usage: `/redeem <credits> <members>`\nExample: `/redeem 100 20`", parse_mode='Markdown')
        return
    try: cr, limit = int(p[1]), int(p[2])
    except: return
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    if "codes" not in db: db["codes"] = {}
    db["codes"][code] = {"credits": cr, "limit": limit, "users": []}
    save_db(db)
    bot.reply_to(m, f"🎟 *CODE CREATED*\nCode: `{code}`\nCredits: `{cr}`\nLimit: `{limit}`\n\nShare:\n`/claim {code}`", parse_mode='Markdown')

@bot.message_handler(commands=['claim'])
def claim_code(m):
    uid, s, p = m.from_user.id, str(m.from_user.id), m.text.split()
    if len(p) != 2:
        bot.reply_to(m, "⚠️ Usage: `/claim CODE`", parse_mode='Markdown')
        return
    c = p[1].strip().upper()
    if "codes" not in db or c not in db["codes"]:
        bot.reply_to(m, "❌ Invalid Code!", parse_mode='Markdown')
        return
    cd = db["codes"][c]
    if s in cd["users"]:
        bot.reply_to(m, "⚠️ Pehle hi claim kar chuke hain!", parse_mode='Markdown')
        return
    if len(cd["users"]) >= cd["limit"]:
        bot.reply_to(m, "⌛ Code Expired!", parse_mode='Markdown')
        return
    u = get_user(uid)
    u["credits"] += cd["credits"]
    cd["users"].append(s)
    save_db(db)
    bot.reply_to(m, f"🎉 *Claimed!* +{cd['credits']} Credits. Total: `{u['credits']}`", parse_mode='Markdown')

@bot.message_handler(commands=['num'])
def search_num(m):
    uid, u = m.from_user.id, get_user(m.from_user.id)
    if not is_joined(uid):
        bot.reply_to(m, "🔒 Pehle channel join karein!", parse_mode='Markdown', reply_markup=join_kb())
        return
    if u["credits"] <= 0:
        bot_info = bot.get_me()
        bot.reply_to(m, f"⚠️ Balance khatam! Refer karein (+3 Credits):\n`https://t.me/{bot_info.username}?start={uid}`", parse_mode='Markdown')
        return
    p = m.text.split()
    if len(p) < 2 or not re.match(r'^[6-9]\d{9}$', p[1].strip()):
        bot.reply_to(m, "⚠️ Sahi format: `/num 9876543210`", parse_mode='Markdown')
        return
    q = p[1].strip()
    wait_msg = bot.reply_to(m, "⚡ *Searching database...*", parse_mode='Markdown')
    try:
        res = requests.get(API_URL, params={"key": API_KEY, "mobile": q}, timeout=15).json()

        name = find_deep(res, ['name', 'Name', 'fullName', 'caller', 'callerName', 'owner', 'user'])
        address = find_deep(res, ['address', 'Address', 'fullAddress', 'location_address', 'street', 'city'])
        carrier = find_deep(res, ['carrier', 'Carrier', 'operator', 'Operator', 'sim', 'network'])
        circle = find_deep(res, ['circle', 'Circle', 'telecom_circle', 'state', 'location', 'region'])
        alt_number = find_deep(res, ['alt_mobile', 'alt_phone', 'alternate_number', 'alt_num'])

        if not name and not address and not carrier and not circle:
            err = res.get('message') or res.get('error') or "Records nahi mile."
            bot.edit_message_text(f"⚠️ {err}", chat_id=m.chat.id, message_id=wait_msg.message_id)
            return

        u["credits"] -= 1
        save_db(db)
        card = (
            f"```text\n"
            f"TARGET DETAILS\n"
            f"------------------------\n"
            f"Phone   : {q}\n"
            f"Name    : {name or 'N/A'}\n"
            f"Address : {address or 'N/A'}\n"
            f"Alt Num : {alt_number or 'None'}\n"
            f"Carrier : {carrier or 'N/A'}\n"
            f"Circle  : {circle or 'India'}\n"
            f"------------------------\n"
            f"Verified by OX\n"
            f"```\n"
            f"💳 Remaining: `{u['credits']} Credits`\n"
            f"👆 *Tap text to copy*"
        )
        bot.edit_message_text(card, chat_id=m.chat.id, message_id=wait_msg.message_id, parse_mode='Markdown')
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {e}", chat_id=m.chat.id, message_id=wait_msg.message_id)

@bot.message_handler(commands=['all'])
def broadcast(m):
    if m.from_user.id != ADMIN_ID: return
    count = 0
    if m.reply_to_message:
        for uid in list(db.keys()):
            if uid == "codes": continue
            try:
                bot.copy_message(int(uid), m.chat.id, m.reply_to_message.message_id)
                count += 1
            except: pass
        bot.reply_to(m, f"✅ Broadcast sent to {count} users.")
        return
    txt = m.text.replace('/all', '', 1).strip()
    if not txt:
        bot.reply_to(m, "⚠️ Reply to any msg with `/all` or type `/all text`")
        return
    for uid in list(db.keys()):
        if uid == "codes": continue
        try:
            bot.send_message(int(uid), f"📢 *ANNOUNCEMENT*\n\n{txt}", parse_mode='Markdown')
            count += 1
        except: pass
    bot.reply_to(m, f"✅ Broadcast sent to {count} users.")

@bot.message_handler(commands=['addcredit'])
def add_cr(m):
    if m.from_user.id != ADMIN_ID: return
    p = m.text.split()
    if len(p) == 3 and p[1] in db:
        db[p[1]]["credits"] += int(p[2])
        save_db(db)
        bot.reply_to(m, f"✅ Added {p[2]} credits to {p[1]}.")

@bot.callback_query_handler(func=lambda c: True)
def callbacks(c):
    uid = c.from_user.id
    if c.data == "verify":
        if is_joined(uid):
            bot.delete_message(c.message.chat.id, c.message.message_id)
            bot.send_message(c.message.chat.id, "✅ Verified! Start searching with `/num <number>`", reply_markup=permanent_kb())
        else:
            bot.answer_callback_query(c.id, "❌ Join nahi mila!", show_alert=True)

if __name__ == '__main__':
    threading.Thread(target=run_web).start()
    bot.infinity_polling()
        
