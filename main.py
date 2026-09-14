import os
import re
import json
import random
import string
import threading
import requests
import telebot
from telebot import types
from flask import Flask

# Background Web Server (Render 24/7)
app = Flask(__name__)

@app.route('/')
def home():
    return "OX TELEGRAM BOT RUNNING 24/7"

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
            "referrals": 0,
            "lang": "hinglish"
        }
        save_db(db)
    elif "lang" not in db[str_id]:
        db[str_id]["lang"] = "hinglish"
        save_db(db)
    return db[str_id]

def is_user_joined(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception:
        return False

# Translations Dictionary
STRINGS = {
    "hinglish": {
        "welcome": (
            "╔══════════════════════╗\n"
            "   ⚡ *OX INTELLIGENCE SYSTEM* ⚡\n"
            "╚══════════════════════╝\n\n"
            "👋 Welcome, *{name}*!\n\n"
            "┌ 💳 *Balance:* `{credits} Credits`\n"
            "├ ⚡ *Cost:* `1 Credit / Search`\n"
            "└ 👥 *Invited:* `{referrals} Users`\n\n"
            "💬 *How to use:*\n"
            "Number search karne ke liye command send karein:\n"
            "👉 `/num <10-digit number>`\n"
            "*(Example: `/num 9876543210`)*\n\n"
            "🎟 *Redeem Code:* `/claim <CODE>`\n\n"
            "────────────────────────\n"
            "👑 *Modded By Rehan* | `@OxRehann`"
        ),
        "channel_lock": (
            "🔒 *ACCESS DENIED*\n"
            "────────────────────────\n"
            "Bot access karne ke liye pehle official channel join karein aur verify par click karein.\n"
            "────────────────────────"
        ),
        "btn_verify": "⚡ Verify Membership",
        "btn_join": "📢 Join Channel",
        "btn_profile": "💳 Balance",
        "btn_refer": "🎁 Refer & Earn",
        "btn_buy": "💎 Buy Credits",
        "btn_support": "💬 Support",
        "btn_lang": "🌐 Language",
        "no_credit": (
            "⚠️ *INSUFFICIENT BALANCE*\n"
            "────────────────────────\n"
            "Aapka lookup credit 0 ho chuka hai.\n\n"
            "• *Free:* Doston ko refer karein (+3 Credits)\n"
            "• *Buy:* Direct admin se buy karein\n\n"
            "🔗 *Your Referral Link:*\n`{ref_link}`"
        ),
        "num_format_err": "⚠️ *Invalid Format!*\nSahi tarika: `/num 9876543210`",
        "searching": "⚡ *Querying secure database...*",
        "not_found": "⚠️ Records database me nahi mile.",
        "verified": "✅ *Verified!* Ab aap bot use kar sakte hain."
    },
    "english": {
        "welcome": (
            "╔══════════════════════╗\n"
            "   ⚡ *OX INTELLIGENCE SYSTEM* ⚡\n"
            "╚══════════════════════╝\n\n"
            "👋 Welcome, *{name}*!\n\n"
            "┌ 💳 *Balance:* `{credits} Credits`\n"
            "├ ⚡ *Cost:* `1 Credit / Search`\n"
            "└ 👥 *Invited:* `{referrals} Users`\n\n"
            "💬 *How to use:*\n"
            "To lookup mobile info, send command:\n"
            "👉 `/num <10-digit number>`\n"
            "*(Example: `/num 9876543210`)*\n\n"
            "🎟 *Redeem Code:* `/claim <CODE>`\n\n"
            "────────────────────────\n"
            "👑 *Modded By Rehan* | `@OxRehann`"
        ),
        "channel_lock": (
            "🔒 *ACCESS DENIED*\n"
            "────────────────────────\n"
            "Please join our official channel below and click verify to access the bot.\n"
            "────────────────────────"
        ),
        "btn_verify": "⚡ Verify Membership",
        "btn_join": "📢 Join Channel",
        "btn_profile": "💳 Balance",
        "btn_refer": "🎁 Refer & Earn",
        "btn_buy": "💎 Buy Credits",
        "btn_support": "💬 Support",
        "btn_lang": "🌐 Language",
        "no_credit": (
            "⚠️ *INSUFFICIENT BALANCE*\n"
            "────────────────────────\n"
            "Your credit balance is exhausted.\n\n"
            "• *Free:* Invite friends (+3 Credits each)\n"
            "• *Buy:* Purchase directly from Admin\n\n"
            "🔗 *Your Referral Link:*\n`{ref_link}`"
        ),
        "num_format_err": "⚠️ *Invalid Format!*\nCorrect usage: `/num 9876543210`",
        "searching": "⚡ *Querying secure database...*",
        "not_found": "⚠️ No records found in database.",
        "verified": "✅ *Verified!* You can now use the bot."
    }
}

def force_join_markup(lang):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(STRINGS[lang]["btn_join"], url=TG_CHANNEL_LINK),
        types.InlineKeyboardButton(STRINGS[lang]["btn_verify"], callback_data="verify_join")
    )
    return markup

def main_menu_markup(lang):
    markup = types.InlineKeyboardMarkup(row_width=2)
    b1 = types.InlineKeyboardButton(STRINGS[lang]["btn_profile"], callback_data="btn_profile")
    b2 = types.InlineKeyboardButton(STRINGS[lang]["btn_refer"], callback_data="btn_refer")
    b3 = types.InlineKeyboardButton(STRINGS[lang]["btn_buy"], callback_data="btn_buy")
    b4 = types.InlineKeyboardButton(STRINGS[lang]["btn_support"], url=f"https://t.me/{ADMIN_USERNAME}")
    b5 = types.InlineKeyboardButton(STRINGS[lang]["btn_lang"], callback_data="btn_lang")
    markup.add(b1, b2)
    markup.add(b3, b4)
    markup.add(b5)
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
                    bot.send_message(
                        int(referrer_id),
                        "🎉 *Referral Success!*\n└ Naye user ne join kiya: *+3 Credits* added!",
                        parse_mode='Markdown'
                    )
                except Exception:
                    pass

        db[str_id] = {
            "credits": 5,
            "referred_by": referrer_id,
            "referrals": 0,
            "lang": "hinglish"
        }
        save_db(db)

    user_data = get_user(user_id)
    lang = user_data.get("lang", "hinglish")

    if not is_user_joined(user_id):
        bot.reply_to(message, STRINGS[lang]["channel_lock"], parse_mode='Markdown', reply_markup=force_join_markup(lang))
        return

    text = STRINGS[lang]["welcome"].format(
        name=message.from_user.first_name,
        credits=user_data['credits'],
        referrals=user_data['referrals']
    )
    bot.reply_to(message, text, parse_mode='Markdown', reply_markup=main_menu_markup(lang))

@bot.message_handler(commands=['redeem'])
def generate_redeem_code(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(
            message,
            "⚠️ *Usage Format:*\n`/redeem <credits> <members>`\n\n*Example:*\n`/redeem 100 20` *(100 credits for 20 users)*",
            parse_mode='Markdown'
        )
        return

    try:
        credits_amount = int(parts[1])
        max_uses = int(parts[2])
    except ValueError:
        bot.reply_to(message, "⚠️ Credits aur Member count numbers hone chahiye!", parse_mode='Markdown')
        return

    random_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    if "redeem_codes" not in db:
        db["redeem_codes"] = {}

    db["redeem_codes"][random_code] = {
        "credits": credits_amount,
        "max_uses": max_uses,
        "claimed_by": []
    }
    save_db(db)

    out = (
        "╔══════════════════════╗\n"
        "   🎟 *REDEEM CODE CREATED* 🎟\n"
        "╚══════════════════════╝\n\n"
        f"🔑 *Code:* `{random_code}`\n"
        f"🎁 *Reward:* `{credits_amount} Credits`\n"
        f"👥 *Total Limit:* `{max_uses} Members`\n\n"
        "📢 *Channel Share Post (Tap to copy):*\n"
        f"```text\n/claim {random_code}\n```\n"
        "────────────────────────\n"
        "👑 *Admin System*"
    )
    bot.reply_to(message, out, parse_mode='Markdown')

@bot.message_handler(commands=['claim'])
def claim_voucher(message):
    user_id = message.from_user.id
    str_id = str(user_id)
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "⚠️ *Usage:* `/claim <CODE>`\n*Example:* `/claim A1B2C3`", parse_mode='Markdown')
        return

    code_entered = parts[1].strip().upper()
    if "redeem_codes" not in db or code_entered not in db["redeem_codes"]:
        bot.reply_to(message, "❌ *Invalid Code!* Aisa koi code active nahi hai.", parse_mode='Markdown')
        return

    code_data = db["redeem_codes"][code_entered]
    if str_id in code_data["claimed_by"]:
        bot.reply_to(message, "⚠️ Aap yeh voucher pehle hi claim kar chuke hain!", parse_mode='Markdown')
        return

    if len(code_data["claimed_by"]) >= code_data["max_uses"]:
        bot.reply_to(message, "⌛ *Code Expired!* Maximum users ki limit poori ho chuki hai.", parse_mode='Markdown')
        return

    user_data = get_user(user_id)
    credit_gift = code_data["credits"]
    user_data["credits"] += credit_gift
    code_data["claimed_by"].append(str_id)
    save_db(db)

    left_slots = code_data["max_uses"] - len(code_data["claimed_by"])
    congrats = (
        "🎉 *CODE CLAIMED SUCCESSFULLY!*\n"
        "────────────────────────\n"
        f"┌ 🎁 *Credits Added:* `+{credit_gift}`\n"
        f"├ 💳 *New Balance:* `{user_data['credits']} Credits`\n"
        f"└ ⚡ *Remaining Slots:* `{left_slots}`\n"
        "────────────────────────"
    )
    bot.reply_to(message, congrats, parse_mode='Markdown')

@bot.message_handler(commands=['num'])
def lookup_number(message):
    user_id = message.from_user.id
    user_data = get_user(user_id)
    lang = user_data.get("lang", "hinglish")

    if not is_user_joined(user_id):
        bot.reply_to(message, STRINGS[lang]["channel_lock"], parse_mode='Markdown', reply_markup=force_join_markup(lang))
        return

    if user_data["credits"] <= 0:
        bot_info = bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
        no_credit_msg = STRINGS[lang]["no_credit"].format(ref_link=ref_link)
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(STRINGS[lang]["btn_refer"], callback_data="btn_refer"),
            types.InlineKeyboardButton(STRINGS[lang]["btn_buy"], url=f"https://t.me/{ADMIN_USERNAME}")
        )
        bot.reply_to(message, no_credit_msg, parse_mode='Markdown', reply_markup=markup)
        return

    parts = message.text.split()
    if len(parts) < 2 or not re.match(r'^[6-9]\d{9}$', parts[1].strip()):
        bot.reply_to(message, STRINGS[lang]["num_format_err"], parse_mode='Markdown')
        return

    query_num = parts[1].strip()
    wait_msg = bot.reply_to(message, STRINGS[lang]["searching"], parse_mode='Markdown')

    try:
        res = requests.get(API_URL, params={"key": API_KEY, "mobile": query_num}, timeout=12)
        data = res.json()

        name = find_deep_value(data, ['name', 'Name', 'fullName', 'caller', 'callerName', 'owner', 'user'])
        address = find_deep_value(data, ['address', 'Address', 'fullAddress', 'location_address', 'street', 'city'])
        carrier = find_deep_value(data, ['carrier', 'Carrier', 'operator', 'Operator', 'sim', 'network'])
        circle = find_deep_value(data, ['circle', 'Circle', 'telecom_circle', 'state', 'location', 'region'])
        alt_number = find_deep_value(data, ['alt_mobile', 'alt_phone', 'alternate_number', 'alt_num', 'alternatePhone'])

        if not name and not carrier and not circle and not address:
            err_msg = data.get('message') or STRINGS[lang]["not_found"]
            bot.edit_message_text(f"⚠️ *{err_msg}*", chat_id=message.chat.id, message_id=wait_msg.message_id, parse_mode='Markdown')
            return

        user_data["credits"] -= 1
        save_db(db)

        copyable_card = (
            f"```text\n"
            f"TARGET INFORMATION\n"
            f"────────────────────────\n"
            f"Phone    : {query_num}\n"
            f"Name     : {name or 'N/A'}\n"
            f"Address  : {address or 'N/A'}\n"
            f"Alt Phone: {alt_number or 'None'}\n"
            f"Carrier  : {carrier or 'N/A'}\n"
            f"Circle   : {circle or 'India'}\n"
            f"────────────────────────\n"
            f"Status   : Verified by OX\n"
            f"```"
        )

        footer_text = (
            f"💳 *Remaining Balance:* `{user_data['credits']} Credits`\n"
            f"👆 *Tip:* Text par tap karke instant copy karein.\n"
            f"────────────────────────\n"
            f"👑 *Modded By Rehan* | `@OxRehann`"
        )

        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(STRINGS[lang]["btn_join"], url=TG_CHANNEL_LINK),
            types.InlineKeyboardButton(STRINGS[lang]["btn_support"], url=f"https://t.me/{ADMIN_USERNAME}")
        )
        bot.edit_message_text(
            f"{copyable_card}\n{footer_text}",
            chat_id=message.chat.id,
            message_id=wait_msg.message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )

    except Exception as e:
        bot.edit_message_text(f"❌ *System Error:* `{str(e)}`", chat_id=message.chat.id, message_id=wait_msg.message_id, parse_mode='Markdown')
@bot.message_handler(commands=['all'])
def broadcast_all(message):
    if message.from_user.id != ADMIN_ID:
        return

    if message.reply_to_message:
        target_msg = message.reply_to_message
        count = 0
        status_msg = bot.reply_to(message, "⏳ *Broadcasting message to all users...*", parse_mode='Markdown')
        for uid in list(db.keys()):
            if uid == "redeem_codes":
                continue
            try:
                bot.copy_message(chat_id=int(uid), from_chat_id=message.chat.id, message_id=target_msg.message_id)
                count += 1
            except Exception:
                pass
        bot.edit_message_text(f"✅ *Broadcast completed!*\nDelivered to `{count}` users.", chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode='Markdown')
        return

    raw_text = message.text.replace('/all', '', 1).strip()
    if not raw_text:
        bot.reply_to(message, "⚠️ *Usage:*\n1. Kisi bhi post par *Reply* karke likhein `/all`\n2. Ya direct likhein: `/all Aapka text yahan`", parse_mode='Markdown')
        return

    count = 0
    status_msg = bot.reply_to(message, "⏳ *Broadcasting text...*", parse_mode='Markdown')
    for uid in list(db.keys()):
        if uid == "redeem_codes":
            continue
        try:
            bot.send_message(int(uid), f"📢 *GLOBAL NOTICE*\n────────────────────────\n{raw_text}\n────────────────────────\n👑 *Admin Announcement*", parse_mode='Markdown')
            count += 1
        except Exception:
            pass
    bot.edit_message_text(f"✅ *Broadcast delivered to `{count}` users.*", chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode='Markdown')

@bot.message_handler(commands=['addcredit'])
def add_credits_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "⚠️ Usage: `/addcredit <user_id> <amount>`", parse_mode='Markdown')
        return
    target_id, amount = parts[1], int(parts[2])
    if target_id in db:
        db[target_id]["credits"] += amount
        save_db(db)
        bot.reply_to(message, f"✅ Added `{amount}` credits to `{target_id}`.", parse_mode='Markdown')
        try:
            bot.send_message(int(target_id), f"🎁 *RECHARGE ALERT*\n└ Admin provided *+{amount} Credits*!", parse_mode='Markdown')
        except Exception:
            pass

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    user_data = get_user(user_id)
    lang = user_data.get("lang", "hinglish")

    if call.data == "verify_join":
        if is_user_joined(user_id):
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, STRINGS[lang]["verified"], parse_mode='Markdown', reply_markup=main_menu_markup(lang))
        else:
            bot.answer_callback_query(call.id, "❌ Channel membership not found!", show_alert=True)

    elif call.data == "btn_lang":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🇮🇳 Hinglish", callback_data="set_lang_hinglish"),
            types.InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_english")
        )
        bot.edit_message_text("🌐 *Choose your preferred language / Bhasha chunein:*", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='Markdown', reply_markup=markup)

    elif call.data.startswith("set_lang_"):
        new_lang = call.data.replace("set_lang_", "")
        user_data["lang"] = new_lang
        save_db(db)
        bot.answer_callback_query(call.id, f"Language set to {new_lang.title()}!")
        text = STRINGS[new_lang]["welcome"].format(
            name=call.from_user.first_name,
            credits=user_data['credits'],
            referrals=user_data['referrals']
        )
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='Markdown', reply_markup=main_menu_markup(new_lang))

    elif call.data == "btn_profile":
        text = (
            "👤 *ACCOUNT OVERVIEW*\n"
            "────────────────────────\n"
            f"┌ 🆔 *Account ID:* `{user_id}`\n"
            f"├ 💳 *Credits:* `{user_data['credits']}`\n"
            f"├ 🌐 *Language:* `{lang.upper()}`\n"
            f"└ 👥 *Referrals:* `{user_data['referrals']}`\n"
            "────────────────────────"
        )
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, text, parse_mode='Markdown')

    elif call.data == "btn_refer":
        bot_info = bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
        text = (
            "🎁 *REFERRAL PROGRAM*\n"
            "────────────────────────\n"
            "Share link with friends to get **+3 Credits** each!\n\n"
            f"🔗 *Your Referral Link:*\n`{ref_link}`\n\n"
            f"👥 *Total Invites:* `{user_data['referrals']}`\n"
            "────────────────────────"
        )
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, text, parse_mode='Markdown')

    elif call.data == "btn_buy":
        text = (
            "💎 *CREDIT RECHARGE*\n"
            "────────────────────────\n"
            "Direct contact to purchase credits:\n"
            f"👉 [@{ADMIN_USERNAME}](https://t.me/{ADMIN_USERNAME})"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💬 Buy via Admin", url=f"https://t.me/{ADMIN_USERNAME}"))
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

if __name__ == '__main__':
    threading.Thread(target=run_web).start()
    bot.infinity_polling()
    
