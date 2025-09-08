import os
    import logging
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    from flask import Flask, request # <-- Добавляем Flask и request

    # Включаем логирование
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)

    # --- КОНСТАНТЫ И ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ---
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    APP_URL = os.getenv("APP_URL")
    PORT = 8080 # Жестко задаем порт

    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable is not set. Exiting.")
        raise ValueError("BOT_TOKEN environment variable is not set.")
    if not APP_URL:
        logger.error("APP_URL environment variable is not set. Please set it to your Timeweb Cloud app URL (e.g., https://my-bot-xxxx.twc1.net). Exiting.")
        raise ValueError("APP_URL environment variable is not set.")

    # --- НАСТРОЙКА TELEGRAM БОТА ---
    # Создаём Application (для telegram-бота)
    telegram_application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики команд
    telegram_application.add_handler(CommandHandler("start", start))
    telegram_application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    telegram_application.add_error_handler(error_handler)

    # --- НАСТРОЙКА FLASK ПРИЛОЖЕНИЯ (ДЛЯ GUNICORN) ---
    # Создаем Flask-приложение, которое будет запускаться Gunicorn-ом
    app = Flask(__name__)

    @app.route("/")
    def index():
        return "Hello from Timeweb Cloud Bot Backend! Waiting for Telegram webhooks. <br>Your bot token URL path: /" + BOT_TOKEN

    @app.route(f"/{BOT_TOKEN}", methods=["POST"])
    async def telegram_webhook_handler():
        # Обработка входящих вебхуков от Telegram
        # Когда Telegram отправляет сообщение, Flask принимает его здесь
        # и передает нашему telegram_application для обработки.
        update = Update.de_json(request.get_json(force=True), telegram_application.bot)
        await telegram_application.process_update(update)return "ok"

    # --- ГЛАВНЫЙ ЗАПУСК ---
    if __name__ == "__main__":
        logger.info("Local run: Starting Flask app and Telegram bot webhook listener...")
        # Устанавливаем вебхук, чтобы Telegram знал, куда отправлять сообщения
        try:
            # Для локального запуска webhook_url может быть другим,
            # но здесь мы используем APP_URL для примера
            # await telegram_application.bot.set_webhook(url=f"{APP_URL}/{BOT_TOKEN}")
            # В данном случае, run_webhook() внутри Flask-приложения будет избыточным.
            # Мы просто устанавливаем вебхук и запускаем Flask.
            # Flask сам будет слушать порт.
            pass # Вебхук будет установлен снаружи или через POST запрос

        except Exception as e:
            logger.error(f"Failed to set webhook on local run: {e}")

        # Запускаем Flask-приложение для локальной отладки.
        # Gunicorn будет использовать 'app' как точку входа.
        app.run(host="0.0.0.0", port=PORT, debug=True)


