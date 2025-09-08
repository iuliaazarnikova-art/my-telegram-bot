import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.mention_html()}! Я простой эхо-робот. Отправь мне сообщение.",
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None:
    # Секретный код твоего робота из Telegram
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    # Адрес домика твоего робота в интернете (мы его узнаем чуть позже)
    APP_URL = os.getenv("APP_URL")
        PORT = 8080

    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен. Робот не может запуститься.")
        return
    if not APP_URL:
        logger.error("APP_URL не установлен. Робот не знает своего адреса в интернете.")
        return

    
    application = Application.builder().token(BOT_TOKEN).build()

    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_error_handler(error_handler)

    
    logger.info("Запускаю робота через вебхуки...")
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN, 
        webhook_url=f"{APP_URL}/{BOT_TOKEN}"
    )
    logger.info("Робот запущен и ждет сообщений!")


if __name__ == "__main__":

    main()

