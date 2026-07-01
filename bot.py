from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import *
from tinydb import TinyDB

from config import BOT_TOKEN, CHANNEL_ID


db = TinyDB("db.json")


# ذخیره آهنگ کانال
async def channel_music(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = update.channel_post

    if not msg:
        return

    if msg.audio or msg.document:

        number = len(db.all()) + 1

        if msg.audio:
            file_id = msg.audio.file_id
            name = msg.audio.file_name

        else:
            file_id = msg.document.file_id
            name = msg.document.file_name


        db.insert({
            "id": number,
            "name": name,
            "file_id": file_id
        })

        print("Saved:", name)



# start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["🎵 آخرین موزیک ها"]
    ]

    await update.message.reply_text(
        "سلام 👋",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )



# آخرین آهنگ ها
async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):

    songs = db.all()

    if not songs:
        await update.message.reply_text(
            "هیچ آهنگی ذخیره نشده ❌"
        )
        return


    text = "🎵 آخرین موزیک ها:\n\n"


    for s in songs[-10:]:
        text += f"{s['id']} - {s['name']}\n"


    await update.message.reply_text(text)



# ارسال با کد
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    for song in db.all():

        if str(song["id"]) == text:

            await update.message.reply_audio(
                song["file_id"],
                caption=song["name"]
            )

            return


    await update.message.reply_text(
        "پیدا نشد ❌"
    )




app = Application.builder().token(BOT_TOKEN).build()


app.add_handler(CommandHandler("start", start))


app.add_handler(
    MessageHandler(
        filters.UpdateType.CHANNEL_POST,
        channel_music
    )
)


app.add_handler(
    MessageHandler(
        filters.Regex("^🎵 آخرین موزیک ها$"),
        latest
    )
)


app.add_handler(
    MessageHandler(
        filters.TEXT,
        search
    )
)


print("RUNNING")

app.run_polling()
