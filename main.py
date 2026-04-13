import asyncio
import time
import os
import logging
from pyrogram import Client, filters
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery
)
from pyrogram.errors import (
    SessionPasswordNeeded, PhoneCodeInvalid,
    PhoneCodeExpired, PasswordHashInvalid,
    PhoneNumberInvalid, FloodWait, ApiIdInvalid,
    UserDeactivated, AuthKeyUnregistered
)

# ═══════════════════════════════════════════════════════════════
#                    LOGGING SETUP
# ═══════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
#                   BOT CONFIGURATION
# ═══════════════════════════════════════════════════════════════

API_ID = 34039354
API_HASH = "e8f8739959e4fbe917f4780c13625543"
BOT_TOKEN = "8758625321:AAHZheX0hulRyRRdf1p_YbSxHpoOHXkm0Yw"
OWNER_ID = 8094093317
LOG_CHANNEL = -1003830365185
SESSION_TIMEOUT = 300

# ═══════════════════════════════════════════════════════════════
#              PREMIUM ANIMATED EMOJI DICTIONARY
# ═══════════════════════════════════════════════════════════════

# ================= NORMAL EMOJI =================
E = {
    "eyes": "👀",
    "smile": "🙂",
    "zap": "⚡️",
    "comet": "☄️",
    "bag": "🛍",
    "nosign": "⛔️",
    "noentry": "🚫",
    "exclaim": "❗️",
    "dblexclaim": "‼️",
    "interro": "⁉️",
    "question": "❓",
    "warning1": "⚠️",
    "warning2": "⚠️",
    "globe": "🌐",
    "chat": "💬",
    "thought": "💭",

    "chart": "📊",
    "check": "✔️",
    "cross": "❌",

    "bell": "🔔",
    "pin": "📌",
    "money1": "💵",
    "money2": "💸",

    "arrow": "➡️",
    "fire": "🔥",
    "boom": "💥",

    "thumbsup": "👍",
    "thumbsdown": "👎",

    "shield": "🛡",
    "link": "🔗",
    "desktop": "🖥",

    "info": "ℹ️",
    "refresh": "🔄",

    "sparkle": "✨",
    "crown": "👑",
    "diamond": "💎",

    "mail": "✉️",
    "lock": "🔒",
    "gear": "⚙️",
    "timer": "⌛️",
}

# ================= PREMIUM EMOJI =================

def em(key: str) -> str:
    premium_map = {
        "eyes": 5210956306952758910,
        "smile": 5461117441612462242,
        "zap": 5456140674028019486,
        "comet": 5224607267797606837,
        "bag": 5229064374403998351,
        "nosign": 5260293700088511294,
        "noentry": 5240241223632954241,
        "exclaim": 5274099962655816924,
        "dblexclaim": 5440660757194744323,
        "interro": 5314504236132747481,
        "question": 5436113877181941026,
        "warning1": 5447644880824181073,
        "warning2": 5420323339723881652,
        "globe": 5447410659077661506,
        "chat": 5443038326535759644,
        "thought": 5467538555158943525,

        "chart": 5231200819986047254,
        "check": 5206607081334906820,
        "cross": 5210952531676504517,

        "bell": 5458603043203327669,
        "pin": 5397782960512444700,
        "money1": 5409048419211682843,
        "money2": 5233326571099534068,

        "arrow": 5416117059207572332,
        "fire": 5424972470023104089,
        "boom": 5276032951342088188,

        "thumbsup": 5337080053119336309,
        "thumbsdown": 5449875686837726134,

        "shield": 5251203410396458957,
        "link": 5271604874419647061,
        "desktop": 5282843764451195532,

        "info": 5334544901428229844,
        "refresh": 5375338737028841420,

        "sparkle": 5325547803936572038,
        "crown": 5217822164362739968,
        "diamond": 5427168083074628963,

        "mail": 5253742260054409879,
        "lock": 5296369303661067030,
        "gear": 5341715473882955310,
        "timer": 5386367538735104399,
    }

    if key in premium_map:
        return f"<emoji id={premium_map[key]}>{E.get(key, '')}</emoji>"

    return E.get(key, "")


# ═══════════════════════════════════════════════════════════════
#                    BOT INITIALIZATION
# ═══════════════════════════════════════════════════════════════
bot = Client(
    name=":memory:",  # 🔥 IMPORTANT
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)
# ═══════════════════════════════════════════════════════════════
#                    GLOBAL VARIABLES
# ═══════════════════════════════════════════════════════════════

users = {}
bot_start_time = time.time()
total_generated = 0
total_users = set()

# ═══════════════════════════════════════════════════════════════
#                   HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_readable_time(seconds: float) -> str:
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    return " ".join(parts)


def progress_bar(step: int, total: int = 5) -> str:
    filled = "█" * step
    empty = "░" * (total - step)
    percent = int((step / total) * 100)
    return f"`[{filled}{empty}]` **{percent}%**"


def get_step_label(step: int) -> str:
    labels = {
        1: f"{em('pin')} Step 1/5",
        2: f"{em('pin')} Step 2/5",
        3: f"{em('pin')} Step 3/5",
        4: f"{em('pin')} Step 4/5",
        5: f"{em('check')} Step 5/5"
    }
    return labels.get(step, f"Step {step}/5")


async def safe_delete(message: Message):
    try:
        await message.delete()
    except Exception:
        pass


async def cleanup_user(user_id: int):
    if user_id in users:
        try:
            client = users[user_id].get("client")
            if client:
                await client.disconnect()
        except Exception:
            pass
        users.pop(user_id, None)


async def check_timeout(user_id: int) -> bool:
    if user_id in users:
        start_time = users[user_id].get("start_time", time.time())
        if time.time() - start_time > SESSION_TIMEOUT:
            await cleanup_user(user_id)
            return True
    return False

# ═══════════════════════════════════════════════════════════════
#                    KEYBOARD LAYOUTS
# ═══════════════════════════════════════════════════════════════

def main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "Generate Session",
                callback_data="generate"
            )
            ], 
        [
            InlineKeyboardButton(
                "Help Guide",
                callback_data="help"
            ),
            InlineKeyboardButton(
                "About Bot",
                callback_data="about"
            )
        ],
        [
            InlineKeyboardButton(
                "Developer",
                url="https://t.me/Abhinav_x06"
            ),
            InlineKeyboardButton(
                "Updates",
                url="https://t.me/AbhinavXupdate"
            )
        ]
    ])


def cancel_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "Cancel Process",
                callback_data="cancel"
            )
        ]
    ])


def back_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "Back to Home",
                callback_data="back_home"
            )
        ]
    ])


def session_type_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "Pyrogram",
                callback_data="pyrogram"
            ),
            InlineKeyboardButton(
                "Telethon",
                callback_data="telethon"
            )
        ],
        [
            InlineKeyboardButton(
                "Back",
                callback_data="back_home"
            )
        ]
    ])


def after_gen_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "Generate Again",
                callback_data="generate"
            )
        ],
        [
            InlineKeyboardButton(
                "Main Menu",
                callback_data="back_home"
            )
        ]
    ])

# ═══════════════════════════════════════════════════════════════
#                    MESSAGE TEMPLATES
# ═══════════════════════════════════════════════════════════════

def start_message(name: str) -> str:
    return f"""
{em('sparkle')} **Advanced String Session Generator** {em('sparkle')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('smile')} Welcome back, **{name}**!

{em('shield')} I generate **Pyrogram** & **Telethon**
string sessions **securely** for your userbots.

{em('diamond')} **Premium Features:**
{em('check')} Secure & Encrypted Process
{em('check')} Fast Generation in Seconds
{em('check')} Sent to Your Saved Messages
{em('check')} Full 2FA Password Support
{em('check')} Auto Timeout Protection
{em('check')} Real-time Step Progress
{em('check')} Smart Error Recovery
{em('check')} Pyrogram + Telethon Support

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('lock')} **Your credentials are NEVER stored!**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('down')} **Select an option below:**
"""


def step_message(session_type: str, step: int, title: str, body: str) -> str:
    icon = em('zap') if session_type == "pyrogram" else em('globe')
    lib = "Pyrogram" if session_type == "pyrogram" else "Telethon"
    return f"""
{icon} **{lib} Session Generator**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{progress_bar(step)}
{get_step_label(step)} — {title}

{body}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('timer')} Session expires in {SESSION_TIMEOUT // 60} minutes
"""

# ═══════════════════════════════════════════════════════════════
#                    START COMMAND
# ═══════════════════════════════════════════════════════════════

@bot.on_message(filters.command("start") & filters.private)
async def start(_, message: Message):
    user_id = message.from_user.id
    total_users.add(user_id)
    await cleanup_user(user_id)

    await message.reply(
        text=start_message(message.from_user.first_name),
        reply_markup=main_keyboard(),
        disable_web_page_preview=True
    )

    try:
        await bot.send_message(
            LOG_CHANNEL,
            f"""
{em('bell')} **New User Started Bot!**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('smile')} **Name:** [{message.from_user.first_name}](tg://user?id={user_id})
{em('pin')} **User ID:** `{user_id}`
{em('chat')} **Username:** @{message.from_user.username or 'None'}
{em('timer')} **Time:** `{time.strftime('%Y-%m-%d %H:%M:%S UTC')}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        )
    except Exception:
        pass

# ═══════════════════════════════════════════════════════════════
#                   CALLBACK HANDLER
# ═══════════════════════════════════════════════════════════════

@bot.on_callback_query()
async def callback_handler(_, query: CallbackQuery):
    global total_generated
    data = query.data
    user_id = query.from_user.id
    total_users.add(user_id)

    # ─────────── GENERATE ───────────
    if data == "generate":
        await query.message.edit_text(
            text=f"""
{em('zap')} **Choose Your Session Type:**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('zap')} **Pyrogram**
{em('check')} Best for Pyrogram userbots
{em('check')} Latest stable library
{em('check')} Recommended choice

{em('globe')} **Telethon**
{em('check')} Best for Telethon userbots
{em('check')} Latest stable library
{em('check')} Alternative option

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('down')} Select your preferred library:
""",
            reply_markup=session_type_keyboard()
        )

    # ─────────── PYROGRAM ───────────
    elif data == "pyrogram":
        await cleanup_user(user_id)
        users[user_id] = {
            "type": "pyrogram",
            "step": "api_id",
            "start_time": time.time()
        }
        await query.message.edit_text(
            text=step_message(
                "pyrogram", 1,
                f"Enter Your **API_ID**",
                f"{em('globe')} Get from: [my.telegram.org](https://my.telegram.org)\n"
                f"{em('pin')} Example: `12345678`\n"
                f"{em('info')} It is a numeric value only"
            ),
            reply_markup=cancel_keyboard(),
            disable_web_page_preview=True
        )

    # ─────────── TELETHON ───────────
    elif data == "telethon":
        await cleanup_user(user_id)
        users[user_id] = {
            "type": "telethon",
            "step": "api_id",
            "start_time": time.time()
        }
        await query.message.edit_text(
            text=step_message(
                "telethon", 1,
                f"Enter Your **API_ID**",
                f"{em('globe')} Get from: [my.telegram.org](https://my.telegram.org)\n"
                f"{em('pin')} Example: `12345678`\n"
                f"{em('info')} It is a numeric value only"
            ),
            reply_markup=cancel_keyboard(),
            disable_web_page_preview=True
        )

    # ─────────── STATUS ───────────
    elif data == "status":
        uptime = get_readable_time(time.time() - bot_start_time)
        await query.message.edit_text(
            text=f"""
{em('chart')} **Bot Statistics**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('timer')} **Uptime:** `{uptime}`
{em('zap')} **Sessions Generated:** `{total_generated}`
{em('smile')} **Total Users:** `{len(total_users)}`
{em('fire')} **Active Processes:** `{len(users)}`
{em('diamond')} **Bot Version:** `3.0 Premium`
{em('check')} **Pyrogram:** `Latest`
{em('check')} **Telethon:** `Latest`
{em('green')} **Status:** Online & Running
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
            reply_markup=back_keyboard()
        )

    # ─────────── HELP ───────────
    elif data == "help":
        await query.message.edit_text(
            text=f"""
{em('question')} **Complete Usage Guide**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('pin')} **Step-by-Step Process:**

{em('play')} **Step 1** — Get API Credentials
{em('check')} Visit [my.telegram.org](https://my.telegram.org)
{em('check')} Login with your phone number
{em('check')} Go to **API Development Tools**
{em('check')} Create app → Get **API_ID** + **API_HASH**

{em('play2')} **Step 2** — Generate Session
{em('check')} Click **Generate Session** button
{em('check')} Choose **Pyrogram** or **Telethon**
{em('check')} Enter API_ID, API_HASH, Phone
{em('check')} Enter OTP with spaces: `1 2 3 4 5`
{em('check')} Enter 2FA password if enabled

{em('play2')} **Step 3** — Get Your Session
{em('check')} Session sent to **Saved Messages**
{em('check')} Copy and use in your userbot!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('shield')} **Safety Guidelines:**
{em('nosign')} Never share session string
{em('nosign')} Never use untrusted bots
{em('check')} Revoke if compromised
{em('check')} Use for YOUR accounts only
{em('check')} Revoke: Settings → Devices

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('gear')} **Commands:**
`/start` `/generate` `/cancel` `/status`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
            reply_markup=back_keyboard(),
            disable_web_page_preview=True
        )

    # ─────────── ABOUT ───────────
    elif data == "about":
        await query.message.edit_text(
            text=f"""
{em('info')} **About This Bot**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('diamond')} **Name:** Advanced String Generator
{em('bookmark')} **Version:** 1.0 Premium
{em('crown')} **Developer:** @Abhinav_x02
{em('gear')} **Built With:** Pyrogram + Telethon
{em('desktop')} **Language:** Python 3.10+

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('shield')} **Security Features:**
{em('lock')} Zero credential storage
{em('lock')} In-memory sessions only
{em('lock')} Auto cleanup after generation
{em('lock')} Timeout protection system
{em('lock')} Secure 2FA password handling

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('loud')} **Updates:** @AbhinavXupdate
{em('star')} **Star us on GitHub!**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
            reply_markup=back_keyboard()
        )

    # ─────────── CANCEL ───────────
    elif data == "cancel":
        await cleanup_user(user_id)
        await query.message.edit_text(
            text=f"""
{em('cross')} **Process Cancelled!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('shield')} Your session generation has been cancelled.
{em('trash')} All temporary data has been cleared.
{em('check')} No credentials were stored.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('zap')} Start fresh anytime below!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "Back to Home",
                        callback_data="back_home"
                    )
                ]
            ])
        )

    # ─────────── BACK HOME ───────────
    elif data == "back_home":
        await query.message.edit_text(
            text=start_message(query.from_user.first_name),
            reply_markup=main_keyboard(),
            disable_web_page_preview=True
        )

    await query.answer()

# ═══════════════════════════════════════════════════════════════
#                  MAIN TEXT HANDLER
# ═══════════════════════════════════════════════════════════════

@bot.on_message(
    filters.text & filters.private &
    ~filters.command([
        "start", "cancel", "generate",
        "ping", "broadcast", "logs", "users"
    ])
)
async def process_steps(_, message: Message):

    user_id = message.chat.id

    # ✅ YAHAN DALNA HAI
    if user_id not in users:
       return

    # 👇 baaki tera logic yahan se continue hoga
    if await check_timeout(user_id):
        return await message.reply(
            f"{em('timer')} **Session Timed Out!**\n\n"
            f"Process must complete within "
            f"{SESSION_TIMEOUT // 60} minutes.\n"
            f"{em('refresh')} Send /start to try again."
        )

    data = users[user_id]
    session_type = data.get("type", "pyrogram")

    try:

        # ════════════════════════════════════
        #          STEP 1: API ID
        # ════════════════════════════════════
        if data.get("step") == "api_id":
            try:
                api_id = int(message.text.strip())
                if api_id <= 0:
                    raise ValueError("Must be positive")
                data["api_id"] = api_id
            except ValueError:
                return await message.reply(
                    f"{em('cross')} **Invalid API_ID!**\n\n"
                    f"{em('exclaim')} Must be a **positive number**\n"
                    f"{em('pin')} Example: `12345678`\n\n"
                    f"{em('refresh')} Please try again:",
                    reply_markup=cancel_keyboard()
                )

            data["step"] = "api_hash"
            await message.reply(
                text=step_message(
                    session_type, 2,
                    "Enter Your **API_HASH**",
                    f"{em('check')} API_ID `{api_id}` saved!\n\n"
                    f"{em('globe')} Get from: [my.telegram.org](https://my.telegram.org)\n"
                    f"{em('pin')} Example: `a3f8b9c2d1e4f5a6b7c8d9e0f1a2b3c4`\n"
                    f"{em('info')} It is a 32-character hex string"
                ),
                reply_markup=cancel_keyboard(),
                disable_web_page_preview=True
            )

        # ════════════════════════════════════
        #          STEP 2: API HASH
        # ════════════════════════════════════
        elif data.get("step") == "api_hash":
            api_hash = message.text.strip()

            if len(api_hash) != 32:
                return await message.reply(
                    f"{em('cross')} **Invalid API_HASH!**\n\n"
                    f"{em('exclaim')} Your input is **{len(api_hash)} chars** long\n"
                    f"{em('exclaim')} Must be exactly **32 characters**\n"
                    f"{em('info')} Only hex characters `a-f`, `0-9`\n\n"
                    f"{em('refresh')} Please try again:",
                    reply_markup=cancel_keyboard()
                )

            if not all(c in '0123456789abcdefABCDEF' for c in api_hash):
                return await message.reply(
                    f"{em('cross')} **Invalid API_HASH Format!**\n\n"
                    f"{em('exclaim')} Contains invalid characters\n"
                    f"{em('check')} Valid: `0-9` and `a-f` only\n\n"
                    f"{em('refresh')} Please try again:",
                    reply_markup=cancel_keyboard()
                )

            data["api_hash"] = api_hash
            data["step"] = "phone"
            await message.reply(
                text=step_message(
                    session_type, 3,
                    "Enter Your **Phone Number**",
                    f"{em('check')} API_HASH saved!\n\n"
                    f"{em('chat')} **Format:** `+CountryCodeNumber`\n"
                    f"{em('pin')} **Examples:**\n"
                    f"  India: `+919876543210`\n"
                    f"  USA: `+12345678900`\n"
                    f"  UK: `+447911123456`"
                ),
                reply_markup=cancel_keyboard()
            )

        # ════════════════════════════════════
        #        STEP 3: PHONE NUMBER
        # ════════════════════════════════════
        elif data.get("step") == "phone":
            phone = message.text.strip()

            if not phone.startswith("+"):
                return await message.reply(
                    f"{em('cross')} **Invalid Phone Format!**\n\n"
                    f"{em('exclaim')} Must start with `+` and country code\n"
                    f"{em('pin')} Example: `+919876543210`\n\n"
                    f"{em('refresh')} Please try again:",
                    reply_markup=cancel_keyboard()
                )

            if len(phone) < 8 or len(phone) > 16:
                return await message.reply(
                    f"{em('cross')} **Invalid Phone Length!**\n\n"
                    f"{em('exclaim')} Number seems too short or too long\n"
                    f"{em('refresh')} Check and try again:",
                    reply_markup=cancel_keyboard()
                )

            data["phone"] = phone
            loading_msg = await message.reply(
                f"{em('timer')} **Connecting to Telegram...**\n"
                f"`Please wait while we send OTP`"
            )

            try:
                if session_type == "pyrogram":
                    client = Client(
                        name=f"session_{user_id}_{int(time.time())}",
                        api_id=data["api_id"],
                        api_hash=data["api_hash"],
                        in_memory=True
                    )
                    await client.connect()
                    sent_code = await client.send_code(phone)
                    data["phone_code_hash"] = sent_code.phone_code_hash
                    data["client"] = client

                elif session_type == "telethon":
                    try:
                        from telethon import TelegramClient
                        from telethon.sessions import StringSession
                    except ImportError:
                        await loading_msg.edit_text(
                            f"{em('cross')} **Telethon Not Installed!**\n\n"
                            f"`pip install telethon`\n\n"
                            f"Contact admin to fix this."
                        )
                        users.pop(user_id, None)
                        return

                    client = TelegramClient(
                        StringSession(),
                        data["api_id"],
                        data["api_hash"]
                    )
                    await client.connect()
                    sent_code = await client.send_code_request(phone)
                    data["phone_code_hash"] = sent_code.phone_code_hash
                    data["client"] = client

                data["step"] = "otp"
                await loading_msg.edit_text(
                    text=step_message(
                        session_type, 4,
                        "Enter the **OTP Code**",
                        f"{em('check')} OTP sent to your Telegram!\n\n"
                        f"{em('exclaim')} **Important:**\n"
                        f"{em('pin')} Send OTP **with spaces**: `1 2 3 4 5`\n"
                        f"{em('pin')} Or without spaces: `12345`\n"
                        f"{em('chat')} Check **Telegram app** for code\n"
                        f"{em('timer')} OTP expires in **2 minutes!**"
                    ),
                    reply_markup=cancel_keyboard()
                )

            except PhoneNumberInvalid:
                data["step"] = "phone"
                await loading_msg.edit_text(
                    f"{em('cross')} **Invalid Phone Number!**\n\n"
                    f"{em('exclaim')} Number not recognized by Telegram\n"
                    f"{em('refresh')} Check format and try again:"
                )

            except ApiIdInvalid:
                await loading_msg.edit_text(
                    f"{em('cross')} **Invalid API Credentials!**\n\n"
                    f"{em('exclaim')} API_ID or API_HASH is incorrect\n"
                    f"{em('refresh')} Send /start and try again."
                )
                await cleanup_user(user_id)

            except FloodWait as e:
                await loading_msg.edit_text(
                    f"{em('warning1')} **Rate Limited by Telegram!**\n\n"
                    f"{em('timer')} Wait **{e.value} seconds** before retrying\n"
                    f"{em('refresh')} Send /start after the wait."
                )
                await cleanup_user(user_id)

            except Exception as e:
                logger.error(f"Phone step error: {e}")
                await loading_msg.edit_text(
                    f"{em('cross')} **Connection Error!**\n\n"
                    f"`{str(e)[:200]}`\n\n"
                    f"{em('refresh')} Send /start to retry."
                )
                await cleanup_user(user_id)

        # ════════════════════════════════════
        #           STEP 4: OTP
        # ════════════════════════════════════
        elif data.get("step") == "otp":
            otp = (
                message.text.strip()
                .replace(" ", "")
                .replace("-", "")
                .replace(".", "")
            )

            if not otp.isdigit():
                return await message.reply(
                    f"{em('cross')} **Invalid OTP Format!**\n\n"
                    f"{em('exclaim')} OTP must contain only numbers\n"
                    f"{em('pin')} Send as: `1 2 3 4 5` or `12345`\n\n"
                    f"{em('refresh')} Please try again:",
                    reply_markup=cancel_keyboard()
                )

            client = data.get("client")
            if not client:
                await message.reply(
                    f"{em('cross')} **Session Expired!**\n"
                    f"{em('refresh')} Send /start to retry."
                )
                users.pop(user_id, None)
                return

            loading_msg = await message.reply(
                f"{em('timer')} **Verifying OTP...**\n"
                f"`Please wait...`"
            )

            try:
                if session_type == "pyrogram":
                    await client.sign_in(
                        phone_number=data["phone"],
                        phone_code_hash=data["phone_code_hash"],
                        phone_code=otp
                    )
                elif session_type == "telethon":
                    await client.sign_in(
                        phone=data["phone"],
                        code=otp,
                        phone_code_hash=data["phone_code_hash"]
                    )

                await generate_string(
                    message, loading_msg, client, data, user_id
                )

            except SessionPasswordNeeded:
                data["step"] = "2fa"
                await loading_msg.edit_text(
                    text=step_message(
                        session_type, 4,
                        "Enter Your **2FA Password**",
                        f"{em('lock')} **Two-Step Verification Detected!**\n\n"
                        f"{em('exclaim')} Your account has 2FA enabled\n"
                        f"{em('shield')} Enter your **cloud password** below\n\n"
                        f"{em('warning1')} This message will be **deleted** for security!"
                    ),
                    reply_markup=cancel_keyboard()
                )

            except PhoneCodeInvalid:
                await loading_msg.edit_text(
                    f"{em('cross')} **Wrong OTP Code!**\n\n"
                    f"{em('exclaim')} The code you entered is incorrect\n"
                    f"{em('refresh')} Please enter the correct OTP:",
                    reply_markup=cancel_keyboard()
                )

            except PhoneCodeExpired:
                await loading_msg.edit_text(
                    f"{em('cross')} **OTP Expired!**\n\n"
                    f"{em('exclaim')} Code expired after 2 minutes\n"
                    f"{em('refresh')} Send /start to generate a new OTP."
                )
                await cleanup_user(user_id)

            except FloodWait as e:
                await loading_msg.edit_text(
                    f"{em('warning1')} **Rate Limited!**\n\n"
                    f"{em('timer')} Wait `{e.value}` seconds and try again."
                )
                await cleanup_user(user_id)

            except Exception as e:
                logger.error(f"OTP step error: {e}")
                await loading_msg.edit_text(
                    f"{em('cross')} **Verification Error!**\n\n"
                    f"`{str(e)[:200]}`\n\n"
                    f"{em('refresh')} Send /start to retry."
                )
                await cleanup_user(user_id)

        # ════════════════════════════════════
        #        STEP 5: 2FA PASSWORD
        # ════════════════════════════════════
        elif data.get("step") == "2fa":
            client = data.get("client")
            if not client:
                await message.reply(
                    f"{em('cross')} **Session Expired!**\n"
                    f"{em('refresh')} Send /start to retry."
                )
                users.pop(user_id, None)
                return

            password = message.text.strip()
            loading_msg = await message.reply(
                f"{em('timer')} **Verifying 2FA Password...**\n"
                f"`Please wait...`"
            )

            await safe_delete(message)

            try:
                if session_type == "pyrogram":
                    await client.check_password(password)
                elif session_type == "telethon":
                    await client.sign_in(password=password)

                await generate_string(
                    message, loading_msg, client, data, user_id
                )

            except PasswordHashInvalid:
                await loading_msg.edit_text(
                    f"{em('cross')} **Wrong 2FA Password!**\n\n"
                    f"{em('exclaim')} The password you entered is incorrect\n"
                    f"{em('refresh')} Please try again:",
                    reply_markup=cancel_keyboard()
                )

            except FloodWait as e:
                await loading_msg.edit_text(
                    f"{em('warning1')} **Rate Limited!**\n\n"
                    f"{em('timer')} Wait `{e.value}` seconds before retrying."
                )
                await cleanup_user(user_id)

            except Exception as e:
                logger.error(f"2FA step error: {e}")
                await loading_msg.edit_text(
                    f"{em('cross')} **2FA Verification Error!**\n\n"
                    f"`{str(e)[:200]}`\n\n"
                    f"{em('refresh')} Send /start to retry."
                )
                await cleanup_user(user_id)

    except FloodWait as e:
        await message.reply(
            f"{em('warning1')} **Global Rate Limit!**\n\n"
            f"{em('timer')} Please wait **{e.value} seconds** before retrying."
        )
        await cleanup_user(user_id)

    except Exception as e:
        logger.error(f"Unexpected error for user {user_id}: {e}")
        await message.reply(
            f"{em('cross')} **Unexpected Error!**\n\n"
            f"`{str(e)[:300]}`\n\n"
            f"{em('refresh')} Send /start to retry."
        )
        await cleanup_user(user_id)

# ═══════════════════════════════════════════════════════════════
#              STRING GENERATION FUNCTION
# ═══════════════════════════════════════════════════════════════

async def generate_string(
    message: Message,
    loading_msg: Message,
    client,
    data: dict,
    user_id: int
):
    global total_generated
    session_type = data.get("type", "pyrogram")

    try:
        if session_type == "pyrogram":
            string_session = await client.export_session_string()
            session_label = f"{em('zap')} Pyrogram"
        elif session_type == "telethon":
            from telethon.sessions import StringSession
            string_session = client.session.save()
            session_label = f"{em('globe')} Telethon"

        me = await client.get_me()
        acc_name = f"{me.first_name or ''} {me.last_name or ''}".strip()
        acc_id = me.id
        acc_username = (
            f"@{me.username}" if me.username else "None"
        )
        acc_phone = (
            me.phone
            if hasattr(me, 'phone') and me.phone
            else data.get("phone", "N/A")
        )

        # ── Update progress message ──
        await loading_msg.edit_text(
            f"""
{em('sparkle')} **Session Generated Successfully!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{progress_bar(5)}

{session_label} **Session Ready!**

{em('smile')} **Account:** `{acc_name}`
{em('pin')} **User ID:** `{acc_id}`
{em('chat')} **Username:** {acc_username}
{em('desktop')} **Phone:** `{acc_phone}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('mail')} **Sending to your Saved Messages...**
"""
        )

        # ── Build saved message ──
        saved_msg_text = f"""
{em('lock')} **{session_label} String Session**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

`{string_session}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('smile')} **Account:** {acc_name}
{em('pin')} **User ID:** `{acc_id}`
{em('chat')} **Username:** {acc_username}
{em('timer')} **Generated:** `{time.strftime('%Y-%m-%d %H:%M:%S UTC')}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('warning1')} **SECURITY WARNING:**
{em('nosign')} NEVER share this with anyone!
{em('nosign')} Anyone with this = full account access!
{em('shield')} Revoke: Telegram → Settings → Devices
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('crown')} Powered By @Abhinav_x02
"""

        sent_to_saved = False
        try:
            await client.send_message("me", saved_msg_text)
            sent_to_saved = True
        except Exception as e:
            logger.error(f"Failed to send to saved messages: {e}")

        # ── Final message ──
        if sent_to_saved:
            await message.reply(
                f"""
{em('sparkle')} **Session Delivered Successfully!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('check')} **Sent to your Saved Messages!**

{em('chat')} Open **Telegram → Saved Messages**
to find your session string.

{em('shield')} Keep it safe — never share it!
{em('lock')} Your security is our priority!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
                reply_markup=after_gen_keyboard()
            )
        else:
            await message.reply(
                f"""
{em('warning1')} **Couldn't Send to Saved Messages!**

Here is your session string directly.
Copy it quickly and **delete this message!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`{string_session}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('trash')} **DELETE THIS MESSAGE AFTER COPYING!**
""",
                reply_markup=after_gen_keyboard()
            )

        # ── Log to channel ──
        try:
            await bot.send_message(
                LOG_CHANNEL,
                f"""
{em('bell')} **New Session Generated!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('smile')} **Requester:** [{message.from_user.first_name}](tg://user?id={message.from_user.id})
{em('pin')} **Requester ID:** `{message.from_user.id}`
{em('chat')} **Requester UN:** @{message.from_user.username or 'None'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('zap')} **Session Type:** {session_label}
{em('smile')} **Account Name:** `{acc_name}`
{em('pin')} **Account ID:** `{acc_id}`
{em('chat')} **Account UN:** {acc_username}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('timer')} **Time:** `{time.strftime('%Y-%m-%d %H:%M:%S UTC')}`
{em('chart')} **Total Generated:** `{total_generated + 1}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            )
        except Exception:
            pass

        total_generated += 1

    except Exception as e:
        logger.error(f"String generation error: {e}")
        await loading_msg.edit_text(
            f"{em('cross')} **Session Generation Failed!**\n\n"
            f"`{str(e)[:300]}`\n\n"
            f"{em('refresh')} Send /start to retry."
        )

    finally:
        try:
            await client.disconnect()
        except Exception:
            pass
        users.pop(user_id, None)

# ═══════════════════════════════════════════════════════════════
#                   QUICK COMMANDS
# ═══════════════════════════════════════════════════════════════

@bot.on_message(filters.command("generate") & filters.private)
async def quick_generate(_, message: Message):
    await cleanup_user(message.chat.id)
    await message.reply(
        f"{em('zap')} **Choose Your Session Type:**",
        reply_markup=session_type_keyboard()
    )


@bot.on_message(filters.command("cancel") & filters.private)
async def cancel_cmd(_, message: Message):
    if message.chat.id in users:
        await cleanup_user(message.chat.id)
        await message.reply(
            f"{em('cross')} **Process Cancelled!**\n\n"
            f"{em('shield')} All data cleared.\n"
            f"{em('refresh')} Send /start to begin again."
        )
    else:
        await message.reply(
            f"{em('warning1')} **No active process to cancel!**\n\n"
            f"{em('zap')} Send /start to begin."
        )
# ═══════════════════════════════════════════════════════════════
#                  OWNER COMMANDS
# ═══════════════════════════════════════════════════════════════

@bot.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast(_, message: Message):
    if not message.reply_to_message:
        return await message.reply(
            f"{em('warning1')} **Usage:** Reply to a message with /broadcast"
        )

    status_msg = await message.reply(
        f"{em('loud')} **Starting broadcast to {len(total_users)} users...**"
    )

    success = 0
    failed = 0

    for uid in list(total_users):
        try:
            await message.reply_to_message.copy(uid)
            success += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1

    await status_msg.edit_text(
        f"""
{em('loud')} **Broadcast Complete!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('check')} **Sent:** `{success}`
{em('cross')} **Failed:** `{failed}`
{em('smile')} **Total:** `{len(total_users)}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    )
@bot.on_message(filters.command("logs") & filters.user(OWNER_ID))
async def logs_cmd(_, message: Message):
    uptime = get_readable_time(time.time() - bot_start_time)
    active_users_info = []

    for uid, udata in users.items():
        step = udata.get("step", "unknown")
        stype = udata.get("type", "unknown")
        elapsed = time.time() - udata.get("start_time", time.time())
        active_users_info.append(
            f"{em('pin')} `{uid}` | {stype} | step: {step} | {int(elapsed)}s"
        )

    active_str = (
        "\n".join(active_users_info)
        if active_users_info
        else f"{em('check')} None"
    )

    await message.reply(
        f"""
{em('desktop')} **Detailed Bot Logs**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('timer')} **Uptime:** `{uptime}`
{em('zap')} **Sessions Generated:** `{total_generated}`
{em('smile')} **Total Users:** `{len(total_users)}`
{em('fire')} **Active Processes:** `{len(users)}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**Active Users:**
{active_str}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    )


@bot.on_message(filters.command("users") & filters.user(OWNER_ID))
async def users_cmd(_, message: Message):
    await message.reply(
        f"""
{em('smile')} **User Statistics**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('chart')} **Total Users:** `{len(total_users)}`
{em('fire')} **Active Now:** `{len(users)}`
{em('zap')} **Sessions Generated:** `{total_generated}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    )
@bot.on_message(filters.command("ping") & filters.private)
async def ping_cmd(_, message: Message):
    start = time.perf_counter()

    bot_user = await bot.get_me()
    uptime = get_readable_time(time.time() - bot_start_time)

    ping_msg = await message.reply(f"{em('zap')} **Pinging...**")

    end = time.perf_counter()
    ping = round((end - start) * 1000)

    await asyncio.sleep(1)

    try:
        await ping_msg.delete()
    except:
        pass

    await message.reply(
        f"""
{em('crown')}{bot_user.mention} **System Stats:**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('zap')} **Latency:** `{ping} ms`
{em('timer')} **Uptime:** `{uptime}`
{em('zap')} **Sessions Generated:** `{total_generated}`
{em('smile')} **Total Users:** `{len(total_users)}`
{em('fire')} **Active Processes:** `{len(users)}`
{em('diamond')} **Bot Version:** `1.0`
{em('check')} **Pyrogram:** `Latest`
{em('check')} **Telethon:** `Latest`
{em('green')} **Status:** Online & Running
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    )

# ═══════════════════════════════════════════════════════════════
#              PERIODIC CLEANUP TASK
# ═══════════════════════════════════════════════════════════════

async def cleanup_expired_sessions():
    while True:
        try:
            expired = []
            for uid, udata in list(users.items()):
                start_time = udata.get("start_time", time.time())
                if time.time() - start_time > SESSION_TIMEOUT:
                    expired.append(uid)

            for uid in expired:
                logger.info(
                    f"Cleaning up expired session for user {uid}"
                )
                await cleanup_user(uid)

        except Exception as e:
            logger.error(f"Cleanup task error: {e}")

        await asyncio.sleep(60)

# ═══════════════════════════════════════════════════════════════
#                   BOT STARTUP
# ═══════════════════════════════════════════════════════════════

async def main():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  🤖 Advanced String Session Bot v3.0")
    print("  ⚡ Pyrogram + 🌐 Telethon Support")
    print("  🔐 Secure Session Generator")
    print("  ✨ Premium Animated Emojis Enabled")
    print("  🚀 Starting up...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    await bot.start()
    asyncio.create_task(cleanup_expired_sessions())

    try:
        await bot.send_message(
            OWNER_ID,
            f"""
{em('green')} **Bot Started Successfully!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{em('diamond')} **Version:** `1.0 Premium`
{em('timer')} **Time:** `{time.strftime('%Y-%m-%d %H:%M:%S UTC')}`
{em('gear')} **Libraries:** Pyrogram + Telethon
{em('sparkle')} **Emojis:** Premium Animated
{em('check')} **Status:** All systems operational
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        )
    except Exception:
        pass

    print("  ✅ Bot is running successfully!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    await asyncio.Event().wait()


if __name__ == "__main__":
    bot.run(main())