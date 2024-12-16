import logging
import json
import os
from aiohttp import ClientSession, CookieJar

# Путь к файлу сессий
USERS_FILE = "users.txt"

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Глобальная переменная для хранения сессий пользователей
user_sessions = {}

# Функция для чтения данных из файла
def read_from_file(session_name=None):
    if not os.path.exists(USERS_FILE):
        return None

    with open(USERS_FILE, "r") as file:
        lines = file.readlines()

    for line in lines:
        session_data = line.strip().split(" | ")

        # Проверка на наличие всех данных
        if len(session_data) != 3:
            logging.warning(f"Некорректная строка в файле: {line.strip()}")
            continue

        if session_name is not None and session_data[0] == session_name:
            owner = session_data[1]
            try:
                cookies = json.loads(session_data[2])  # Пробуем распарсить куки
            except json.JSONDecodeError:
                logging.error(f"Ошибка при парсинге JSON для сессии {session_name}: {session_data[2]}")
                return None  # Возвращаем None, если JSON не валиден
            return {"session_name": session_data[0], "owner": owner, "cookies": cookies}

        if session_name is None:
            owner = session_data[1]
            try:
                cookies = json.loads(session_data[2])
            except json.JSONDecodeError:
                logging.error(f"Ошибка при парсинге JSON для сессии {session_data[0]}: {session_data[2]}")
                continue
            if owner not in user_sessions:
                user_sessions[owner] = {}
            user_sessions[owner][session_data[0]] = {
                "owner": owner,
                "cookies": cookies,
                "active": False
            }

    return None

# Функция для записи данных в файл
def write_to_file():
    with open(USERS_FILE, "w") as file:
        for owner, session_data in user_sessions.items():
            for session_name, data in session_data.items():
                cookies_json = json.dumps(data["cookies"])
                file.write(f"{session_name} | {owner} | {cookies_json}\n")
    logging.info(f"Сессии сохранены в файл {USERS_FILE}.")

# Функция для добавления новой сессии
async def add_session(update, context):
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

        # Создаём объект CookieJar для хранения и отправки куков
        jar = CookieJar()
        for cookie in cookies:
            jar.update_cookies({cookie['name']: cookie['value']})

        session = ClientSession(cookie_jar=jar)
        await session.__aenter__()

        # Сохраняем сессию и куки для пользователя
        if update.message.from_user.username not in user_sessions:
            user_sessions[update.message.from_user.username] = {}

        if session_name in user_sessions[update.message.from_user.username]:
            await update.message.reply_text(f"Сессия с именем {session_name} уже существует.")
        else:
            user_sessions[update.message.from_user.username][session_name] = {
                "session": session,
                "active": False,
                "owner": update.message.from_user.username,
                "cookies": cookies
            }

            # Записываем данные в файл
            write_to_file()
            await update.message.reply_text(f"Сессия {session_name} успешно добавлена!")
            logging.info(f"Сессия {session_name} добавлена для пользователя {update.message.from_user.username}.")

    except json.JSONDecodeError:
        await update.message.reply_text("Невозможно распарсить куки. Убедитесь, что они в формате JSON.")
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")

# Команда для удаления сессии
async def remove_session(update, context):
    user_id = update.message.from_user.id
    if len(context.args) < 1:
        await update.message.reply_text("Использование: /del <имя_сессии>")
        return

    session_name = context.args[0]

    if user_id in user_sessions and session_name in user_sessions[user_id]:
        session = user_sessions[user_id].pop(session_name)
        await session["session"].__aexit__(None, None, None)
        await update.message.reply_text(f"Сессия {session_name} удалена.")
        write_to_file()  # Сохраняем изменения в файл
    else:
        await update.message.reply_text(f"Сессия с именем {session_name} не найдена.")

# Команда для получения владельца сессии и куков
async def get_user(update, context):
    user_id = update.message.from_user.id
    if user_id not in ALLOWED_USER_IDS:
        await update.message.reply_text("У вас нет прав на использование этой команды.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Использование: /get_user <имя_сессии>")
        return

    session_name = context.args[0]

    session_info = read_from_file(session_name)
    if session_info:
        owner = session_info["owner"]
        cookies_text = json.dumps(session_info["cookies"], indent=4)  # Преобразуем куки в красивый формат

        response = f"Сессия: {session_name}\n"
        response += f"Владелец: {owner}\n"
        response += f"Куки: {cookies_text}"

        await update.message.reply_text(response)
    else:
        await update.message.reply_text(f"Сессия с именем {session_name} не найдена.")
