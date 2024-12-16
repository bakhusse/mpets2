import os
import json
import logging

# Путь к файлу сессий
USERS_FILE = "users.txt"

# Разрешенные пользователи по ID
ALLOWED_USER_IDS = [1811568463, 630965641]

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Глобальная переменная для хранения сессий пользователей
user_sessions = {}

# Функция для чтения данных из файла
def read_from_file(session_name):
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

        if session_data[0] == session_name:
            owner = session_data[1]
            try:
                cookies = json.loads(session_data[2])  # Пробуем распарсить куки
            except json.JSONDecodeError:
                logging.error(f"Ошибка при парсинге JSON для сессии {session_name}: {session_data[2]}")
                return None  # Возвращаем None, если JSON не валиден
            return {"session_name": session_data[0], "owner": owner, "cookies": cookies}

    return None

# Функция для записи данных в файл
def write_to_file(session_name, owner, cookies):
    with open(USERS_FILE, "a") as file:
        cookies_json = json.dumps(cookies)
        file.write(f"{session_name} | {owner} | {cookies_json}\n")
    logging.info(f"Сессия {session_name} добавлена в файл.")

# Функция для отображения всех сессий пользователя
def list_sessions(user_id):
    if user_id in user_sessions and user_sessions[user_id]:
        session_list = "\n".join([f"{name} - {'Активна' if session['active'] else 'Неактивна'}"
                                 for name, session in user_sessions[user_id].items()])
        return f"Ваши активные сессии:\n{session_list}"
    else:
        return "У вас нет активных сессий."

# Добавление и удаление сессий
# Эти функции предполагаются уже в вашем коде:
def add_session(user_id, session_name, cookies):
    # Реализация добавления сессии
    pass

def remove_session(user_id, session_name):
    # Реализация удаления сессии
    pass
