import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- (Остальной код бота, который начинается с logging.basicConfig до def main() ---

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.mention_html()}! Я простой эхо-робот. Отправь мне сообщение.",
    )

# Обработчик обычных текстовых сообщений (эхо)
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)

# Обработчик ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None: # <-- Эта функция ОСТАЕТСЯ, но НЕ ВЫЗЫВАЕТСЯ НАПРЯМУЮ
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable is not set. Exiting.")
        return

    # Создаём Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_error_handler(error_handler)

    # Запускаем через long polling
    logger.info("Starting bot with long polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    logger.info("Bot stopped.")


# --- ВОТ ЭТОТ НОВЫЙ БЛОК ВМЕСТО if __name__ == "__main__": main() ---
if __name__ == "__main__":
    import time
    import threading

    # Функция, которая будет запускать бота в отдельном потоке
    def run_bot():
        main() # <-- Здесь мы вызываем нашу функцию main()

    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    logger.info("Main process started. Bot is running in a separate thread. Keeping main process alive...")

    # Основной процесс просто висит, чтобы Timeweb Cloud думал, что приложение работает
    try:
        while True:
            time.sleep(3600) # Ждем 1 час, потом проверяем
    except KeyboardInterrupt:
        logger.info("Main process interrupted.")
        bot_thread.join() # Ждем завершения потока бота


