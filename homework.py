import logging
import os
import sys
import time

import requests
import telegram
from dotenv import load_dotenv

from exceptions import *

load_dotenv()


PRACTICUM_TOKEN = os.getenv('pr_token')
TELEGRAM_TOKEN = os.getenv('tel_token')
TELEGRAM_CHAT_ID = os.getenv('tel_chat_id')

logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s - %(name)s'
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправляем сообщение в чат."""
    return bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def get_api_answer(current_timestamp):
    """Получаем ответ от API."""
    timestamp = current_timestamp# or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code != 200:
        logger.error('API не отвечает на запрос')
        raise ResponseStatusCodeError
    logger.info('Отправлен API запрос')
    response = response.json()
    print(response)
    return response


def check_response(response):
    """Проверяем ответ от API."""
    if type(response) is not dict:
        raise ApiResponseTypeError.__name__
    elif type(response.get('homeworks')) is not list:
        raise HomeworkTypeError
    else:
        homework = response.get('homeworks')
        print(homework)
        return homework


def parse_status(homework):
    """Получаем данные о домашней работе."""
    for works in homework:
        if not 'homework_name':
            logger.error('В ответе API отсутствет ключ homework_name')
        elif not 'status':
            logger.error('В ответе API отсутствет ключ status')
            raise HomeworkStatusError
        else:
            homework_name = homework.get('homework_name')
            homework_status = homework.get('status')
            verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяем переменные окружения."""
    check_result = True
    if (not PRACTICUM_TOKEN or
            not TELEGRAM_TOKEN or
            not TELEGRAM_CHAT_ID):
        check_result = False
        logger.critical('Отсутствет переменная окружения!')
    elif (PRACTICUM_TOKEN is not None
          and TELEGRAM_TOKEN is not None
          and TELEGRAM_CHAT_ID is not None):
        check_result = True
    return check_result


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = 1645994703# int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            status = homework.get('status')
            if status in HOMEWORK_STATUSES:
                message = parse_status(homework)
                send_message(bot, message)
            current_timestamp = current_timestamp - RETRY_TIME
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            logger.info('Сообщение об ошибке отправлено в Телеграм')
            time.sleep(RETRY_TIME)
        else:
            pass


if __name__ == '__main__':
    main()
