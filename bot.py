from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import *
from tinydb import TinyDB


db = TinyDB("db.json")

from config import BOT_TOKEN, CHANNEL_ID


# ذخیره آهنگ کانال
async def channel_music(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.id != CHANNEL_ID:
        return

    msg = update.message

    if msg.audio or msg.document:

        count = len(db.all()) + 1

        name = (
            msg.audio.file_name
            if msg.audio
            else msg.document.file_name
        )

        db.insert({
            "id": count,
            "file_id": msg.audio.file_id if msg.audio else msg.document.file_id,
            "name": name
        })


# شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    menu = [
        ["🎵 آخرین موزیک ها"],
        ["🔎 جستجو"]
    ]

    await update.message.reply_text(
        "سلام 👋\nکد یا اسم آهنگ رو بفرست",
        reply_markup=ReplyKeyboardMarkup(menu, resize_keyboard=True)
    )


# ارسال آهنگ با کد یا سرچ
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    result = None


    if text.isdigit():

        for song in db.all():
            if song["id"] == int(text):
                result = song
                break


    else:

        for song in db.all():

            if text.lower() in song["name"].lower():
                result = song
                break



    if result:

        await update.message.reply_audio(
            audio=result["file_id"],
            caption=result["name"]
        )

    else:

        await update.message.reply_text(
            "❌ چیزی پیدا نشد"
        )



app = Application.builder().token(BOT_TOKEN).build()


app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(
        filters.ChatType.CHANNEL,
        channel_music
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT,
        search
    )
)


print("Bot Started")

app.run_polling()
