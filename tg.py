import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import nest_asyncio
import json
from session import add_session, remove_session, list_sessions
from game import get_pet_stats, auto_actions

# Установите ваш токен бота
TOKEN = "7690678050:AAGBwTdSUNgE7Q6Z2LpE6481vvJJhetrO-4"

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Команда старт для начала работы с ботом
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Привет! Управляй сессиями с помощью команд:\n"
                                    "/add - добавить новую сессию\n"
                                    "/del - удалить сессию\n"
                                    "/list - посмотреть все сессии\n"
                                    "/on - активировать сессию\n"
                                    "/off - деактивировать сессию\n"
                                    "/stats <имя_сессии> - проверить статистику питомца\n"
                                    "/get_user <имя_сессии> - узнать владельца сессии и куки")

# Команда для добавления новой сессии
async def add(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    try:
        if len(context.args) < 2:
            await update.message.reply_text("Использование: /add <имя_сессии> <куки в формате JSON>")
            return

        session_name = context.args[0]
        cookies_json = " ".join(context.args[1:])
        
        cookies = json.loads(cookies_json)
        if not cookies:
            await update.message.reply_text("Пожалуйста, отправьте куки в правильном формате JSON.")
            return

        # Добавляем сессию
        if add_session(user_id, session_name, cookies):
            await update.message.reply_text(f"Сессия {session_name} успешно добавлена!")
        else:
            await update.message.reply_text(f"Сессия с именем {session_name} уже существует.")
    except json.JSONDecodeError:
        await update.message.reply_text("Невозможно распарсить куки. Убедитесь, что они в формате JSON.")
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")

# Команда для удаления сессии
async def remove(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if len(context.args) < 1:
        await update.message.reply_text("Использование: /del <имя_сессии>")
        return

    session_name = context.args[0]

    if remove_session(user_id, session_name):
        await update.message.reply_text(f"Сессия {session_name} удалена.")
    else:
        await update.message.reply_text(f"Сессия с именем {session_name} не найдена.")

# Команда для отображения всех сессий
async def list(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    response = list_sessions(user_id)
    await update.message.reply_text(response)

# Основная функция для запуска бота
async def main():
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add))
    application.add_handler(CommandHandler("del", remove))
    application.add_handler(CommandHandler("list", list))

    # Запуск бота
    await application.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()  # Это позволяет использовать event loop в Jupyter или других средах, где он уже запущен
    asyncio.get_event_loop().run_until_complete(main())
