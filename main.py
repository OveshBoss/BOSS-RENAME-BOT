import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import ffmpeg

api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("BOT_TOKEN")
owner = os.environ.get("OWNER_ID")
channel = os.environ.get("CHANNEL_USERNAME")
start_image = os.environ.get("START_IMAGE")

app = Client("rename-bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)


# ------------------ START COMMAND ------------------

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):

    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📢 ᴏᴜʀ ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{channel}")],
            [InlineKeyboardButton("👑 ᴏᴡɴᴇʀ", url=f"https://t.me/{owner}")]
        ]
    )

    caption = (
        "**ʜᴇʏ ᴛʜᴇʀᴇ 👋\n"
        "ɪ ᴀᴍ ᴀ ᴘᴏᴡᴇʀꜰᴜʟ ʀᴇɴᴀᴍᴇ + ᴄᴏɴᴠᴇʀᴛ ʙᴏᴛ ᴡɪᴛʜ ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇꜱ ⚡**"
        "\n\n"
        "“🌟 ʀᴇɴᴀᴍᴇ ᴀɴʏ ꜰɪʟᴇ ɪɴ ꜱᴇᴄᴏɴᴅꜱ\n"
        "📺 ᴀᴜᴛᴏ ᴠɪᴅᴇᴏ ʀᴇᴄᴏᴅᴇ / ᴄᴏɴᴠᴇʀᴛ\n"
        "🖼 ᴄᴜꜱᴛᴏᴍ ᴛʜᴜᴍʙɴᴀɪʟ ꜱᴜᴘᴘᴏʀᴛ\n"
        "📤 ꜰᴀꜱᴛ ᴜᴘʟᴏᴀᴅ ꜱᴘᴇᴇᴅ\n"
        "🔐 ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ ᴏɴʟʏ — ꜱᴀꜰᴇ & ꜱᴇᴄᴜʀᴇ”"
    )

    try:
        await message.reply_photo(start_image, caption=caption, reply_markup=buttons)
    except:
        await message.reply_text(caption, reply_markup=buttons)


# ------------------ SAVE THUMBNAIL ------------------

@app.on_message(filters.photo & filters.private)
async def save_thumb(client, message):
    os.makedirs("thumb", exist_ok=True)
    path = f"thumb/{message.from_user.id}.jpg"
    await message.download(path)
    await message.reply_text("✅ ᴛʜᴜᴍʙɴᴀɪʟ ꜱᴀᴠᴇᴅ ꜱᴜᴄᴄᴇꜱꜰᴜʟʟʏ!")


# ------------------ MAIN RENAME + CONVERT ------------------

@app.on_message(filters.private & (filters.document | filters.video))
async def rename_handler(client, message):

    media = message.document or message.video

    await message.reply_text(
        f"📄 **ᴏʟᴅ ɴᴀᴍᴇ:** `{media.file_name}`\n\n"
        "📝 **ꜱᴇɴᴅ ɴᴇᴡ ꜰɪʟᴇ ɴᴀᴍᴇ (ᴡɪᴛʜ ᴇxᴛᴇɴꜱɪᴏɴ)**"
    )

    new_msg = await client.listen(message.chat.id)
    new_name = new_msg.text

    msg = await message.reply("⬇ **ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ꜰɪʟᴇ...**")

    original = await client.download_media(media)
    new_file = f"downloads/{new_name}"
    os.makedirs("downloads", exist_ok=True)

    # if video → convert using ffmpeg
    if media.mime_type.startswith("video"):
        await msg.edit("🎞 **ᴄᴏɴᴠᴇʀᴛɪɴɢ ᴠɪᴅᴇᴏ...**")

        (
            ffmpeg
            .input(original)
            .output(new_file, vcodec='libx264', acodec='aac')
            .run(overwrite_output=True)
        )
        os.remove(original)

    else:
        os.rename(original, new_file)

    # load thumbnail if available
    thumb_path = f"thumb/{message.from_user.id}.jpg"
    thumb = thumb_path if os.path.exists(thumb_path) else None

    await msg.edit("⬆ **ᴜᴘʟᴏᴀᴅɪɴɢ...**")

    await message.reply_document(
        new_file,
        caption="✔ **ꜰɪʟᴇ ᴘʀᴏᴄᴇꜱꜱᴇᴅ ꜱᴜᴄᴄᴇꜱꜰᴜʟʟʏ!**",
        thumb=thumb
    )

    os.remove(new_file)


# ------------------ RUN APP ------------------

app.run()

