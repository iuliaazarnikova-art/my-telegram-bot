import os
    import logging
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    from flask import Flask, request # Добавляем Flask для совместимости с gunicorn

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

    # --- ВОТ ЭТА ЧАСТЬ ИЗМЕНИЛАСЬ СУЩЕСТВЕННО! ---

    BOT_TOKEN = os.getenv("BOT_TOKEN")
    APP_URL = os.getenv("APP_URL")
    PORT = 8080 # Жестко задаем порт

    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable is not set. Exiting.")
        raise ValueError("BOT_TOKEN environment variable is not set.")
    if not APP_URL:
        logger.error("APP_URL environment variable is not set. Please set it to your Timeweb Cloud app URL (e.g., https://my-bot-xxxx.twc1.net). Exiting.")
        raise ValueError("APP_URL environment variable is not set.")

    # Создаём Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_error_handler(error_handler)

    # Создаем минимальное Flask-приложение
    # Это приложение будет запускаться Gunicorn-ом
    # А наш Telegram-бот будет работать через вебхуки внутри этого же процесса
    app = Flask(__name__)

    @app.route("/")
    def hello_world():
        return "Hello from Timeweb Cloud Bot Backend! Waiting for Telegram webhooks."

    @app.route(f"/{BOT_TOKEN}", methods=["POST"])
    async def telegram_webhook():
        # Обработка входящих вебхуков от Telegram
        # Это код из документации python-telegram-bot для вебхуков
        update = Update.de_json(request.get_json(force=True), application.bot)
        awaitapplication.process_update(update)
        return "ok"

    # Теперь в главном блоке запускаем Flask-приложение,
    # и оно будет запускать webhook-сервер в фоновом режиме.
    if __name__ == "__main__":
        logger.info("Starting Flask app and Telegram bot webhook listener...")
        # Устанавливаем вебхук при старте, если он еще не установлен
        # Эту часть можно вынести в отдельный скрипт, но для простоты оставим здесь
        # application.run_webhook() запускает небольшой веб-сервер внутри
        # Но gunicorn уже будет слушать порт. Поэтому мы должны быть осторожны.
        # Правильный подход: Flask слушает, а Telegram.ext обрабатывает запросы через Flask.

        # Запускаем Flask приложение.
        # !!! Важно: flask_app.run() здесь не нужен, так как Gunicorn запускает app !!!
        # Мы просто должны убедиться, что bot.set_webhook вызывается
        logger.info(f"Setting webhook to: {APP_URL}/{BOT_TOKEN}")
        # Здесь мы используем синхронную версию set_webhook, так как это не в async функции
        # Но run_webhook сам устанавливает вебхук, так что это лишнее,
        # если мы обрабатываем через Flask роут.
        # application.bot.set_webhook(url=f"{APP_URL}/{BOT_TOKEN}")

        # Запуск Flask-приложения (Gunicorn будет его запускать)
        app.run(host="0.0.0.0", port=PORT, debug=False) # Эта строка для ЛОКАЛЬНОГО запуска, Gunicorn её игнорирует


