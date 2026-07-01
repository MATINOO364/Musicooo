from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import *
from tinydb import TinyDB

from config import BOT_TOKEN


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




# شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["🎵 آخرین موزیک ها"],
        ["🔎 جستجو"]
    ]


    await update.message.reply_text(
        "سلام 👋\nآهنگتو پیدا کن",
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
            "هیچ آهنگی نداریم ❌"
        )

        return



    buttons = []


    for song in songs[-10:]:

        buttons.append([

            InlineKeyboardButton(
                f"🎵 {song['name']}",
                callback_data=str(song["id"])
            )

        ])



    await update.message.reply_text(

        "آخرین موزیک‌ها:",

        reply_markup=InlineKeyboardMarkup(buttons)

    )





# ارسال آهنگ با دکمه
async def send_song(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()



    song_id = int(query.data)



    for song in db.all():


        if song["id"] == song_id:


            await query.message.reply_audio(

                audio=song["file_id"],

                caption=song["name"]

            )


            return





# سرچ با کد
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()



    for song in db.all():


        if str(song["id"]) == text:


            await update.message.reply_audio(

                audio=song["file_id"],

                caption=song["name"]

            )

            return




    await update.message.reply_text(
        "❌ پیدا نشد"
    )






app = Application.builder().token(BOT_TOKEN).build()



# start
app.add_handler(
    CommandHandler(
        "start",
        start
    )
)



# کانال
app.add_handler(

    MessageHandler(

        filters.UpdateType.CHANNEL_POST,

        channel_music

    )

)



# دکمه آخرین موزیک

app.add_handler(

    MessageHandler(

        filters.Regex("^🎵 آخرین موزیک ها$"),

        latest

    )

)



# کلیک روی آهنگ

app.add_handler(

    CallbackQueryHandler(

        send_song

    )

)



# پیام معمولی

app.add_handler(

    MessageHandler(

        filters.TEXT,

        search

    )

)



print("BOT RUNNING")


app.run_polling()
