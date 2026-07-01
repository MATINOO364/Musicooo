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

async def channel_music(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = update.channel_post


    if not msg:
        return


    if msg.audio or msg.document:


        song_id = database.song_count() + 1


        if msg.audio:

            file_id = msg.audio.file_id
            name = msg.audio.file_name


        else:

            file_id = msg.document.file_id
            name = msg.document.file_name



        database.add_song({

            "id": song_id,

            "name": name,

            "file_id": file_id

        })


        print("Saved:", name)





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
