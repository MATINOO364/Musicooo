from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import *
from tinydb import TinyDB

from config import BOT_TOKEN, CHANNEL_ID


db = TinyDB("db.json")


# گرفتن آهنگ از کانال
async def channel_music(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.id != CHANNEL_ID:
        return

    msg = update.effective_message

    if msg.audio or msg.document:

        count = len(db.all()) + 1

        name = (
            msg.audio.file_name
            if msg.audio
            else msg.document.file_name
        )

        file_id = (
            msg.audio.file_id
            if msg.audio
            else msg.document.file_id
        )

        db.insert({
            "id": count,
            "name": name,
            "file_id": file_id
        })



# استارت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["🎵 آخرین موزیک ها"]
    ]

    await update.message.reply_text(
        "سلام 👋\nکد یا اسم آهنگ رو بفرست",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )



# آخرین موزیک ها
async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):

    songs = db.all()

    if not songs:
        await update.message.reply_text(
            "هنوز آهنگی ذخیره نشده 🎵"
        )
        return


    text = "🎵 آخرین موزیک ها:\n\n"


    for song in songs[-10:]:

        text += f"🔹 {song['id']} - {song['name']}\n"


    await update.message.reply_text(text)



# جستجو و ارسال آهنگ
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
            "❌ آهنگ پیدا نشد"
        )




app = Application.builder().token(BOT_TOKEN).build()



app.add_handler(
    CommandHandler(
        "start",
        start
    )
)


# آهنگ های کانال
app.add_handler(
    MessageHandler(
        filters.ALL,
        channel_music
    )
        )



# دکمه آخرین موزیک ها
app.add_handler(
    MessageHandler(
        filters.Regex("^🎵 آخرین موزیک ها$"),
        latest
    )
)



# سرچ
app.add_handler(
    MessageHandler(
        filters.TEXT,
        search
    )
)



print("Bot Started")

app.run_polling()

