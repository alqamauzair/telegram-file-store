import os
import asyncio
from threading import Thread
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# 1. Background Web Server (24/7 Keep-Alive)
web_app = Flask('')

@web_app.route('/')
def home():
    return "Bot is alive 24/7!"

def run_web_server():
    web_app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web_server)
    t.start()

# 2. Main Bot Configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))
ADMINS = [int(x) for x in os.environ.get("ADMINS", "").split()]
CHANNEL_LINK = "https://t.me/+0_H-_k_crWQzZmI1"

app = Client("FileStoreBot", bot_token=BOT_TOKEN, api_id=6, api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e")
user_sessions = {}

# Commands logic
@app.on_message(filters.command("start"))
async def start_command(client, message):
    if len(message.command) > 1:
        param = message.command[1]
        try:
            if "-" in param:
                first_id, last_id = map(int, param.split("-"))
                await message.reply_text("📦 *Aapki batch files send ki jaa rahi hain...*")
                for msg_id in range(first_id, last_id + 1):
                    try:
                        await client.copy_message(chat_id=message.chat.id, from_chat_id=CHANNEL_ID, message_id=msg_id)
                        await asyncio.sleep(0.5)
                    except: continue
            else:
                await client.copy_message(chat_id=message.chat.id, from_chat_id=CHANNEL_ID, message_id=int(param))
        except Exception:
            await message.reply_text("❌ Links invalid hain ya file delete ho chuki hai.")
    else:
        await message.reply_text("👋 Hello! Mujhe files bhejye, main unka shareable link bana dunga.")

@app.on_message(filters.command("help"))
async def help_command(client, message):
    await message.reply_text(
        f"👋 **Help Center!**\n\nIs bot ka use karke aap files store kar sakte hain.\n\n🔗 **Hamara Official Channel:**\n[Click Here to Join]({CHANNEL_LINK})",
        disable_web_page_preview=True
    )

@app.on_message(filters.private & (filters.text & filters.regex("^✅$")))
async def finish_batch(client, message):
    if message.from_user.id not in ADMINS: return
    user_id = message.from_user.id
    if user_id in user_sessions and user_sessions[user_id]:
        first_id, last_id = min(user_sessions[user_id]), max(user_sessions[user_id])
        user_sessions.pop(user_id)
        bot_username = (await client.get_me()).username
        share_link = f"https://t.me/{bot_username}?start={first_id}" if first_id == last_id else f"https://t.me/{bot_username}?start={first_id}-{last_id}"
        await message.reply_text(
            f"✅ **Upload complete!**\nShare this link:\n`{share_link}`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Open Link", url=share_link)]])
        )

@app.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def handle_files(client, message):
    if message.from_user.id not in ADMINS: return
    user_id = message.from_user.id
    saved_msg = await message.copy(chat_id=CHANNEL_ID)
    if user_id not in user_sessions: user_sessions[user_id] = []
    user_sessions[user_id].append(saved_msg.id)
    finish_keyboard = ReplyKeyboardMarkup([[KeyboardButton("✅")]], resize_keyboard=True, one_time_keyboard=True)
    await message.reply_text("✅ Media saved. Send more or type ✅ to finish.", reply_markup=finish_keyboard)

if __name__ == "__main__":
    print("Starting Web Server...")
    keep_alive()
    print("Master Bot is running with Help command...")
    app.run()
