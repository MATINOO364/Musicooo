from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import *
from config import BOT_TOKEN, ADMIN_ID, CHANNEL_ID
import database


app = Application.builder().token(BOT_TOKEN).build()



# ذخیره کاربر
async def save_user(update: Update):
    if update.effective_user:
        database.add_user(update.effective_user.id)



# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await save_user(update)

    kb = [
        ["🎵 آخرین موزیک ها"],
        ["🔎 جستجو"],
        ["📊 آمار"]
    ]

    if update.effective_user.id == ADMIN_ID:
        kb.append(["👑 پنل ادمین"])

    await update.message.reply_text(
        "🎧 خوش آمدی",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )



# دریافت آهنگ از کانال + دادن کد
async def channel_music(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = update.channel_post
    if not msg or not msg.audio:
        return

    code = database.next_code()

    database.add_song({
        "code": code,
        "name": msg.audio.file_name,
        "file_id": msg.audio.file_id
    })

    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=f"🎵 کد آهنگ: {code}",
        reply_to_message_id=msg.message_id
    )



# آخرین آهنگ‌ها
async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):

    songs = database.all_songs()

    if not songs:
        return await update.message.reply_text("هیچ آهنگی نیست")

    text = "🎵 لیست آهنگ‌ها:\n\n"

    for s in songs[-10:]:
        text += f"{s['code']} - {s['name']}\n"

    await update.message.reply_text(text)



# سرچ + ارسال آهنگ با کد
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    # اگر عدد بود = کد آهنگ
    if text.isdigit():

        song = database.find_by_code(int(text))

        if song:
            return await update.message.reply_audio(
                audio=song["file_id"],
                caption=song["name"]
            )

        return await update.message.reply_text("پیدا نشد ❌")

    # اگر اسم بود
    results = database.search_by_name(text)

    if results:

        text_res = "نتایج:\n\n"

        for r in results[:10]:
            text_res += f"{r['code']} - {r['name']}\n"

        return await update.message.reply_text(text_res)

    await update.message.reply_text("چیزی پیدا نشد ❌")



# آمار
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        f"📊 آمار\n\n🎵 آهنگ‌ها: {database.songs_count()}\n👤 کاربران: {database.users_count()}"
    )



# پنل ادمین
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        "👑 پنل ادمین\n\n"
        f"🎵 آهنگ‌ها: {database.songs_count()}\n"
        f"👤 کاربران: {database.users_count()}"
    )



# HANDLERS
app.add_handler(CommandHandler("start", start))

app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, channel_music))

app.add_handler(MessageHandler(filters.Regex("^🎵 آخرین موزیک ها$"), latest))

app.add_handler(MessageHandler(filters.Regex("^📊 آمار$"), stats))

app.add_handler(MessageHandler(filters.Regex("^👑 پنل ادمین$"), admin))

app.add_handler(MessageHandler(filters.TEXT, handle_text))


print("BOT RUNNING")

app.run_polling()
