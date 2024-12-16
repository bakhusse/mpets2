import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import logging
from session import add_session, remove_session, list_sessions, activate_session, deactivate_session, get_user
from game import get_pet_stats, auto_actions

# Установите ваш токен бота
TOKEN = "7690678050:AAGBwTdSUNgE7Q6Z2LpE6481vvJJhetrO-4"

# Разрешенные пользователи по ID
ALLOWED_USER_IDS = [1811568463, 630965641]

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Функция для отправки сообщений
async def send_message(update: Update, text: str):
    await update.message.reply_text(text)

# Команда старт для начала работы с ботом
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Привет! Управляй сессиями с помощью команд:\n"
                                    "/add - добавить новую сессию\n"
                                    "/del - удалить сессию\n"
                                    "/list - посмотреть все сессии\n"
                                    "/on - активировать сессию\n"
                                    "/off - деактивировать сессию\n"
                                    "/stats <имя_сессии> - проверить статистику питомца\n"
                                    "/get_user <имя_сессии> - узнать владельца сессии и куки\n"
                                    "Отправьте куки в формате JSON для авторизации.")

# Основная функция для запуска бота
async def main():
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_session))
    application.add_handler(CommandHandler("del", remove_session))
    application.add_handler(CommandHandler("list", list_sessions))
    application.add_handler(CommandHandler("on", activate_session))
    application.add_handler(CommandHandler("off", deactivate_session))
    application.add_handler(CommandHandler("stats", get_pet_stats))
    application.add_handler(CommandHandler("get_user", get_user))

    # Запуск бота
    await application.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()  # Это позволяет использовать event loop в Jupyter или других средах, где он уже запущен
    asyncio.get_event_loop().run_until_complete(main())
