from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import *

from config import BOT_TOKEN, ADMIN_ID

import database



app = Application.builder().token(BOT_TOKEN).build()



# ذخیره کاربر
async def save_user(update: Update):

    if update.effective_user:

        database.add_user(
            update.effective_user.id
        )



# شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await save_user(update)


    buttons = [

        ["🎵 آخرین موزیک ها"],

        ["🔎 جستجو"],

        ["📊 آمار"]

    ]


    if update.effective_user.id == ADMIN_ID:

        buttons.append(
            ["👑 پنل ادمین"]
        )



    await update.message.reply_text(

        "سلام 👋\nبه ربات موزیک خوش آمدید",

        reply_markup=ReplyKeyboardMarkup(

            buttons,

            resize_keyboard=True

        )

    )# دریافت آهنگ از کانال
async def channel_music(update, context):

    msg = update.channel_post


    if msg.audio:


        code = database.get_next_id()


        database.add_song({

            "code":code,

            "name":msg.audio.file_name,

            "file_id":msg.audio.file_id

        })


        await context.bot.send_message(

            chat_id=CHANNEL_ID,

            text=f"🎵 کد آهنگ: {code}",

            reply_to_message_id=msg.message_id

        )


        print("Saved", code)





# نمایش آخرین آهنگ‌ها

async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):


    songs = database.get_songs()


    if not songs:

        await update.message.reply_text(
            "هنوز آهنگی ثبت نشده ❌"
        )

        return



    buttons = []


    for song in songs[-10:]:


        buttons.append([

            InlineKeyboardButton(

                song["name"],

                callback_data=str(song["id"])

            )

        ])




    await update.message.reply_text(

        "🎵 آخرین موزیک ها:",

        reply_markup=InlineKeyboardMarkup(buttons)

    )





# ارسال آهنگ با دکمه

async def send_song(update: Update, context: ContextTypes.DEFAULT_TYPE):


    query = update.callback_query

    await query.answer()



    song = database.find_song(

        int(query.data)

    )


    if song:


        await query.message.reply_audio(

            song["file_id"],

            caption=song["name"]

        )
        # آمار

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(

        f"📊 آمار ربات\n\n"
        f"🎵 تعداد آهنگ‌ها: {database.song_count()}\n"
        f"👤 کاربران: {database.user_count()}"

    )





# پنل ادمین

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):


    if update.effective_user.id != ADMIN_ID:

        return



    await update.message.reply_text(

        "👑 پنل ادمین\n\n"
        "🎵 آهنگ‌ها: " + str(database.song_count()) +
        "\n👤 کاربران: " + str(database.user_count())

    )





# سرچ با کد

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):


    text = update.message.text.strip()


    if text.isdigit():


        song = database.find_song(

            int(text)

        )


        if song:


            await update.message.reply_audio(

                song["file_id"],

                caption=song["name"]

            )

            return



    await update.message.reply_text(

        "❌ پیدا نشد"

    )





# اتصال دستورات


app.add_handler(

    CommandHandler(

        "start",

        start

    )

)



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

        filters.Regex("^📊 آمار$"),

        stats

    )

)



app.add_handler(

    MessageHandler(

        filters.Regex("^👑 پنل ادمین$"),

        admin_panel

    )

)



app.add_handler(

    CallbackQueryHandler(

        send_song

    )

)



app.add_handler(

    MessageHandler(

        filters.TEXT,

        search

    )

)



print("BOT STARTED")

app.run_polling()
