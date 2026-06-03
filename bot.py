import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))
ADMINS = [int(x) for x in os.environ.get("ADMINS", "").split()]

app = Client("FileStoreBot", bot_token=BOT_TOKEN, api_id=6, api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e")

# Users ke chal rahe sessions ko track karne ke liye dictionary
user_sessions = {}

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
                    except:
                        continue
            else:
                await client.copy_message(chat_id=message.chat.id, from_chat_id=CHANNEL_ID, message_id=int(param))
        except Exception as e:
            await message.reply_text("❌ Links invalid hain ya file delete ho chuki hai.")
    else:
        await message.reply_text("👋 Hello! Mujhe koi bhi file bhejye, main uska shareable link bana dunga.")

@app.on_message(filters.private & (filters.text & filters.regex("^✅$")))
async def finish_batch(client, message):
    if message.from_user.id not in ADMINS:
        return
    user_id = message.from_user.id
    
    if user_id in user_sessions and user_sessions[user_id]:
        first_id = min(user_sessions[user_id])
        last_id = max(user_sessions[user_id])
        user_sessions.pop(user_id) # Session khatam
        
        bot_username = (await client.get_me()).username
        
        # Link generation format (Single file ho ya multiple, perfectly range handle hogi)
        if first_id == last_id:
            share_link = f"https://t.me/{bot_username}?start={first_id}"
        else:
            share_link = f"https://t.me/{bot_username}?start={first_id}-{last_id}"
            
        # Reply keyboard ko wapas remove karne ke liye
        await message.reply_text(
            f"✅ **Upload complete!**\nShare this link:\n`{share_link}`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Open Link", url=share_link)]])
        )
    else:
        await message.reply_text("❌ Aapki list abhi khali hai. Pehle koi file bhejin.")

@app.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def handle_files(client, message):
    if message.from_user.id not in ADMINS:
        return
    user_id = message.from_user.id
    
    # File ko channel mein save karna
    saved_msg = await message.copy(chat_id=CHANNEL_ID)
    
    # Agar user ka session pehle se nahi hai, toh naya banayein
    if user_id not in user_sessions:
        user_sessions[user_id] = []
        
    user_sessions[user_id].append(saved_msg.id)
    
    # Shortcut finish button (Green Tick) user ke keyboard par show karne ke liye
    finish_keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("✅")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    # Bilkul screenshot jaisa message aur button text
    await message.reply_text(
        "✅ Media saved. Send more or type ✅ to finish.",
        reply_markup=finish_keyboard
    )

print("Interactive Bot is running...")
app.run()
