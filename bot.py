
# bot.py — Telegram bot
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = ""  # Вставь токен
ADMIN_CHAT_ID = 7749088892

user_cooldown = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_text = "Бот работает. Отправьте фото + текст."
    await update.message.reply_text(start_text)

async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_time = datetime.now()

    if user_id in user_cooldown:
        time_diff = current_time - user_cooldown[user_id]
        if time_diff < timedelta(hours=24):
            remaining = timedelta(hours=24) - time_diff
            hours = int(remaining.seconds / 3600)
            minutes = int((remaining.seconds % 3600) / 60)
            await update.message.reply_text(f"❌ Новое объявление можно отправить через {hours}ч {minutes}м")
            return

    if not update.message.caption or len(update.message.caption) < 10:
        await update.message.reply_text("❌ Добавьте текст объявления от 10 символов.")
        return

    username = f"@{update.effective_user.username}" if update.effective_user.username else "Не указан"
    user_profile_link = f"tg://user?id={user_id}"

    caption = f"{update.message.caption}\n\nНаписать автору: [{username}]({user_profile_link})"

    disclaimer = "\n\nВажно! Будьте внимательны. 18+"
    full_text = caption + disclaimer

    admin_keyboard = [
        [InlineKeyboardButton("Подать объявление", url="https://t.me/New_post_vape_bot")],
        [InlineKeyboardButton("Реклама", url="https://t.me/Manager_Greshnik")]
    ]
    reply_markup = InlineKeyboardMarkup(admin_keyboard)

    await context.bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=update.message.photo[-1].file_id,
        caption=full_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

    user_cooldown[user_id] = current_time
    await update.message.reply_text("✅ Объявление отправлено на модерацию!")

async def handle_invalid_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Отправьте одну фотографию + текст (не менее 10 символов).")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Ошибка: {context.error}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO & filters.CAPTION, handle_photo_message))
    app.add_handler(MessageHandler(filters.ALL, handle_invalid_message))
    app.add_error_handler(error_handler)

    print("Bot started…")
    app.run_polling()

if __name__ == "__main__":
    main()
