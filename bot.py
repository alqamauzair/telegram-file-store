import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))
ADMINS = [int(x) for x in os.environ.get("ADMINS", "").split()]

app = Client("FileStoreBot", bot_token=BOT_TOKEN, api_id=6, api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e")

@app.on_message(filters.command("start"))
async def start_command(client, message):
    if len(message.command) > 1:
        file_id = message.command[1]
        try:
            await client.copy_message(chat_id=message.chat.id, from_chat_id=CHANNEL_ID, message_id=int(file_id))
        except Exception as e:
            await message.reply_text("❌ Yeh file delete ho chuki hai ya link invalid hai.")
    else:
        await message.reply_text("👋 Hello! Mujhe koi bhi file bhejye, main uska shareable link bana dunga.")

@app.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def handle_files(client, message):
    if message.from_user.id not in ADMINS:
        await message.reply_text("⛔ Sirf admin hi files upload kar sakta hai.")
        return
    saved_msg = await message.copy(chat_id=CHANNEL_ID)
    bot_username = (await client.get_me()).username
    share_link = f"https://t.me/{bot_username}?start={saved_msg.id}"
    await message.reply_text(
        f"✅ **File saved successfully!**\n\n🔗 **Share this link:**\n`{share_link}`",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Open Link", url=share_link)]])
    )

print("Bot is running...")
app.run()
