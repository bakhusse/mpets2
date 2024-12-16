import asyncio
import logging
from aiohttp import ClientSession
from bs4 import BeautifulSoup

# Функция для получения статистики питомца
async def get_pet_stats(session: ClientSession):
    url = "https://mpets.mobi/profile"
    async with session.get(url) as response:
        if response.status != 200:
            return f"Ошибка при загрузке страницы профиля: {response.status}"

        page = await response.text()
    soup = BeautifulSoup(page, 'html.parser')

    # Парсим страницу, чтобы извлечь информацию о питомце
    stat_items = soup.find_all('div', class_='stat_item')
    
    if not stat_items:
        return "Не удалось найти элементы статистики."

    pet_name = stat_items[0].find('a', class_='darkgreen_link')
    if not pet_name:
        return "Не удалось найти имя питомца."
    pet_name = pet_name.text.strip()

    pet_level = stat_items[0].text.split(' ')[-2]  # Уровень питомца

    experience = "Не найдено"
    for item in stat_items:
        if 'Опыт:' in item.text:
            experience = item.text.strip().split('Опыт:')[-1].strip()
            break

    beauty = "Не найдено"
    for item in stat_items:
        if 'Красота:' in item.text:
            beauty = item.text.strip().split('Красота:')[-1].strip()
            break

    coins = "Не найдено"
    for item in stat_items:
        if 'Монеты:' in item.text:
            coins = item.text.strip().split('Монеты:')[-1].strip()
            break

    hearts = "Не найдено"
    for item in stat_items:
        if 'Сердечки:' in item.text:
            hearts = item.text.strip().split('Сердечки:')[-1].strip()
            break

    vip_status = "Не найдено"
    for item in stat_items:
        if 'VIP-аккаунт:' in item.text:
            vip_status = item.text.strip().split('VIP-аккаунт:')[-1].strip()
            break

    stats = f"Никнейм и уровень: {pet_name}, {pet_level} уровень\n"
    stats += f"Опыт: {experience}\nКрасота: {beauty}\n"
    stats += f"Монеты: {coins}\nСердечки: {hearts}\n"
    stats += f"VIP-аккаунт/Премиум-аккаунт: {vip_status}"

    return stats

# Функция для автоматических действий
async def auto_actions(session, session_name):
    actions = [
        "https://mpets.mobi/?action=food",
        "https://mpets.mobi/?action=play",
        "https://mpets.mobi/show",
        "https://mpets.mobi/glade_dig",
        "https://mpets.mobi/show_coin_get"
    ]

    while True:
        # Перейдем по ссылкам 6 раз для первых 4-х
        for i in range(6):
            for action in actions[:4]:
                await visit_url(session, action, session_name)
                await asyncio.sleep(1)

        # Один раз по пятой ссылке
        await visit_url(session, actions[4], session_name)

        # Переход по дополнительным ссылкам
        for i in range(10, 0, -1):
            url = f"https://mpets.mobi/go_travel?id={i}"
            await visit_url(session, url, session_name)
            await asyncio.sleep(1)

        # Задержка 1 минута перед новым циклом
        await asyncio.sleep(60)

async def visit_url(session, url, session_name):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                logging.info(f"[{session_name}] Переход по {url} прошел успешно!")
            else:
                logging.error(f"[{session_name}] Ошибка при переходе по {url}: {response.status}")
    except Exception as e:
        logging.error(f"[{session_name}] Ошибка при запросе к {url}: {e}")
