import os
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==========================
# SMALL CAPS FONT FUNCTION
# ==========================
def small(text):
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    smallcaps = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ" + "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"
    return text.translate(str.maketrans(normal, smallcaps))


# =====================================
# TELEGRAM CREDENTIALS (FROM ENV)
# =====================================
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


# ==========================
# START COMMAND
# ==========================
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    caption = small(
        "👋 HEY THERE!\n\n"
        "I AM A POWERFUL RENAME + CONVERT BOT WITH PREMIUM FEATURES ⚡\n\n"
        "⭐ RENAME ANY FILE IN SECONDS\n"
        "🎥 AUTO VIDEO RECODE / CONVERT\n"
        "🖼️ CUSTOM THUMBNAIL SUPPORT\n"
        "🚀 SUPER FAST UPLOAD SPEED\n"
        "🔐 PRIVATE CHAT ONLY — SAFE & SECURE"
    )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton(small("📢 OUR CHANNEL"), url=f"https://t.me/{CHANNEL_USERNAME}")],
        [InlineKeyboardButton(small("👑 OWNER"), url=f"https://t.me/{OWNER_ID}")]
    ])

    await message.reply_photo(
        photo=START_IMAGE,
        caption=caption,
        reply_markup=buttons
    )


# ==========================
# MEDIA INFO HANDLER
# ==========================
@app.on_message(filters.private & (filters.document | filters.video))
async def media_info(client, message):

    media = message.document or message.video
    file_name = media.file_name
    file_size = media.file_size
    mime = media.mime_type
    dc_id = media.dc_id

    reply_text = small(
        f"MEDIA INFO\n\n"
        f"◈ OLD FILE NAME: {file_name}\n"
        f"◈ EXTENSION: {mime.split('/')[-1].upper()}\n"
        f"◈ FILE SIZE: {file_size} bytes\n"
        f"◈ MIME TYPE: {mime}\n"
        f"◈ DC ID: {dc_id}\n\n"
        f"PLEASE ENTER THE NEW FILENAME WITH EXTENSION AND REPLY THIS MESSAGE…"
    )

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(small("📄 DOCUMENT"), callback_data="doc"),
            InlineKeyboardButton(small("🎬 VIDEO"), callback_data="vid")
        ]
    ])

    await message.reply_text(reply_text, reply_markup=buttons, quote=True)


# ==========================================
# STORE USER CHOICE (DOC / VIDEO)
# ==========================================
user_choice = {}


@app.on_callback_query()
async def cb_handler(client, query):
    if query.data == "doc":
        user_choice[query.from_user.id] = "document"
        await query.answer(small("DOCUMENT SELECTED"))
        await query.message.reply(small("ENTER NEW FILENAME WITH EXTENSION…"), quote=True)

    if query.data == "vid":
        user_choice[query.from_user.id] = "video"
        await query.answer(small("VIDEO SELECTED"))
        await query.message.reply(small("ENTER NEW FILENAME WITH EXTENSION…"), quote=True)


# ==========================================
# PROGRESS FUNCTION (basic, humanize-free)
# ==========================================
async def progress(current, total, message, start_time):
    now = time.time()
    speed = current / (now - start_time) if (now - start_time) != 0 else 0
    percentage = current * 100 / total if total != 0 else 0
    eta = (total - current) / speed if speed != 0 else 0

    bar = "▢" * int(percentage / 5)

    text = small(
        f"DOWNLOAD STARTED...\n\n"
        f"{bar}\n\n"
        f"╭━━━━❰ST BOTS PROCESSING...❱━➣\n"
        f"┣⪼ SIZE: {current}/{total} BYTES\n"
        f"┣⪼ DONE: {round(percentage, 2)}%\n"
        f"┣⪼ SPEED: {round(speed, 2)} BYTES/S\n"
        f"┣⪼ ETA: {round(eta)} SEC\n"
        f"╰━━━━━━━━━━━━━━━➣"
    )

    try:
        await message.edit(text)
    except:
        pass


# ==========================================
# RENAME HANDLER (USER SENDS NEW NAME)
# ==========================================
@app.on_message(filters.private & filters.reply)
async def rename_handler(client, message):

    if message.reply_to_message and (
        message.reply_to_message.document or message.reply_to_message.video
    ):
        media = message.reply_to_message.document or message.reply_to_message.video
        new_name = message.text

        processing = await message.reply(small("DOWNLOAD STARTED..."))
        start = time.time()

        # DOWNLOAD
        downloaded = await media.download(
            file_name=new_name,
            progress=progress,
            progress_args=(processing, start)
        )

        # UPLOAD
        file_type = user_choice.get(message.from_user.id, "document")
        if file_type == "video":
            await message.reply_video(downloaded)
        else:
            await message.reply_document(downloaded)

        os.remove(downloaded)
        await processing.edit(small("✔️ DONE! FILE UPLOADED SUCCESSFULLY"))


# =====================
# START BOT
# =====================
app.run()

