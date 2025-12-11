import os
import time
import humanize
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# -----------------------------
# SMALL CAPS FONT CONVERTER
# -----------------------------
def small(text):
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    smallcaps = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ" + "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"
    return text.translate(str.maketrans(normal, smallcaps))


# -----------------------------
# ENV VARIABLES (RENDER)
# -----------------------------
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

OWNER_ID = os.getenv("OWNER_ID")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
START_IMAGE = os.getenv("START_IMAGE")

app = Client(
    "RenameBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


# -----------------------------
# /START COMMAND
# -----------------------------
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):

    caption = f"""
👋 **HEY THERE!**

**I AM A POWERFUL RENAME + CONVERT BOT WITH PREMIUM FEATURES ⚡**

“⭐ RENAME ANY FILE IN SECONDS  
🎥 AUTO VIDEO RECODE / CONVERT  
🖼️ CUSTOM THUMBNAIL SUPPORT  
🚀 SUPER FAST UPLOAD SPEED  
🔐 PRIVATE CHAT ONLY — SAFE & SECURE”
"""

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 OUR CHANNEL", url=f"https://t.me/{https://t.me/OveshBossOfficial}")],
        [InlineKeyboardButton("👑 OWNER", url=f"https://t.me/{1416433622}")]
    ])

    await message.reply_photo(
        START_IMAGE,
        caption=caption,
        reply_markup=buttons
    )


# -----------------------------
# MEDIA INFO HANDLER
# -----------------------------
@app.on_message(filters.private & (filters.document | filters.video))
async def media_info(client, message):

    media = message.document or message.video
    file_name = media.file_name
    file_size = humanize.naturalsize(media.file_size)
    mime = media.mime_type
    dc_id = media.dc_id

    info = f"""
**{small("media info")}**

◈ **{small("old file name")}**: `{file_name}`
◈ **{small("extension")}**: `{mime.split('/')[-1].upper()}`
◈ **{small("file size")}**: {file_size}
◈ **{small("mime type")}**: `{mime}`
◈ **{small("dc id")}**: `{dc_id}`

{small("please enter the new filename with extension and reply this message…")}
"""

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📄 DOCUMENT", callback_data="doc"),
            InlineKeyboardButton("🎬 VIDEO", callback_data="vid")
        ]
    ])

    await message.reply_text(info, reply_markup=buttons, quote=True)


# -----------------------------
# STORE DOC/VIDEO CHOICE
# -----------------------------
user_choice = {}


@app.on_callback_query()
async def cb_handler(client, query):

    if query.data == "doc":
        user_choice[query.from_user.id] = "document"
        await query.answer("Document selected ✔")
        await query.message.reply(small("enter new filename with extension…"), quote=True)

    if query.data == "vid":
        user_choice[query.from_user.id] = "video"
        await query.answer("Video selected ✔")
        await query.message.reply(small("enter new filename with extension…"), quote=True)


# -----------------------------
# PROGRESS BAR FUNCTION
# -----------------------------
async def progress(current, total, message, start):
    now = time.time()
    speed = current / (now - start)
    percent = current * 100 / total
    eta = (total - current) / speed if speed > 0 else 0

    bar = "▢" * int(percent / 5)

    text = f"""
**Download Started…**

{bar}

╭━━━━❰ST BOTS PROCESSING...❱━➣
┣⪼ 🗃️ ꜱɪᴢᴇ: {humanize.naturalsize(current)} | {humanize.naturalsize(total)}
┣⪼ ⏳️ ᴅᴏɴᴇ : {round(percent,2)}%
┣⪼ 🚀 ꜱᴩᴇᴇᴅ: {humanize.naturalsize(speed)}/s
┣⪼ ⏰️ ᴇᴛᴀ: {round(eta)} sec
╰━━━━━━━━━━━━━━━➣
"""

    try:
        await message.edit(text)
    except:
        pass


# -----------------------------
# RENAME HANDLER
# -----------------------------
@app.on_message(filters.private & filters.reply)
async def rename_handler(client, message):

    if not message.reply_to_message:
        return

    media = message.reply_to_message.document or message.reply_to_message.video
    new_name = message.text

    processing = await message.reply(small("download started…"))

    start = time.time()

    # -----------------------------
    # DOWNLOAD TO /tmp (RENDER SAFE)
    # -----------------------------
    temp_path = f"/tmp/{new_name}"

    downloaded = await client.download_media(
        message.reply_to_message,
        file_name=temp_path,
        progress=progress,
        progress_args=(processing, start)
    )

    file_type = user_choice.get(message.from_user.id, "document")

    # -----------------------------
    # UPLOAD RENAME RESULT
    # -----------------------------
    if file_type == "video":
        await message.reply_video(downloaded)
    else:
        await message.reply_document(downloaded)

    os.remove(downloaded)
    await processing.edit("✔ **DONE! FILE UPLOADED SUCCESSFULLY**")


# -----------------------------
# START BOT
# -----------------------------
app.run()

