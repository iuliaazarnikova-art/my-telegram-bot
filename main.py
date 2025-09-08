import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Включаем логирование (дневник робота)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Когда кто-то говорит /start, робот отвечает "Привет!"
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.mention_html()}! Я простой эхо-робот. Отправь мне сообщение.",
    )

# Когда кто-то отправляет любое сообщение, робот отправляет его обратно (эхо)
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)

# Если что-то пошло не так, робот запишет это в свой дневник
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None:
    BOT_TOKEN = os.getenv("BOT_TOKEN") # Секретный код твоего робота из Telegram

    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable is not set. Exiting.")
        return

    # Собираем робота
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем команды, которые робот понимает
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_error_handler(error_handler)

    # Запускаем робота через Long Polling (он сам будет спрашивать Telegram о новых сообщениях)
    logger.info("Запускаю робота через Long Polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    logger.info("Робот остановлен.")

if __name__ == "__main__":
    main()


