import http
import logging
import os
import sys
import time

import requests
import telegram
from dotenv import load_dotenv
from telegram import TelegramError

from exceptions import EnvVariableError, ResponseStatusCodeError
from exceptions import HomeworkStatusError


load_dotenv()

PRACTICUM_TOKEN = os.getenv('pr_token')
TELEGRAM_TOKEN = os.getenv('tel_token')
TELEGRAM_CHAT_ID = os.getenv('tel_chat_id')

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s - %(name)s'
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
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
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        message_sent = True
        logger.info('Сообщение отправлено в Телеграм')
    except telegram.error.TelegramError as error:
        logger.error(f'Ошибка отправки сообщения в телеграм: {error}')
        raise TelegramError(f'Ошибка отправки сообщения в телеграм: {error}')
    except Exception as error:
        raise Exception(f'Непредвиденная ошибка: {error}')

    return message_sent


def get_api_answer(current_timestamp):
    """Получаем ответ от API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)

    if response.status_code != http.HTTPStatus.OK:
        logger.error('API не отвечает на запрос')
        raise ResponseStatusCodeError

    logger.info('Отправлен API запрос')
    response = response.json()

    return response


def check_response(response):
    """Проверяем ответ от API."""
    if not isinstance(response, dict):
        logger.error('Ответ API не является словарем')
        raise TypeError('Ответ API не является словарем')
    elif not isinstance(response.get('homeworks'), list):
        logger.error('Список домашних работ не является списком')
        raise TypeError('Список домашних работ не является списком')
    else:
        homeworks = response.get('homeworks')

    return homeworks


def parse_status(homework):
    """Получаем данные о домашней работе."""
    if homework.get('homework_name') is None:
        logger.error('В ответе API отсутствет ключ homework_name')
    homework_name = homework.get('homework_name')

    if homework.get('status') is None:
        logger.error('В ответе API отсутствует ключ status')
        raise HomeworkStatusError
    homework_status = homework.get('status')

    if homework.get('status') not in HOMEWORK_STATUSES:
        logger.error('Недокументированный статус работы')

    verdict = HOMEWORK_STATUSES[homework_status]

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяем переменные окружения."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    status_message = ''
    error_message = ''

    while True:
        try:
            is_tokens = check_tokens()
            if not is_tokens:
                raise EnvVariableError

            response = get_api_answer(current_timestamp)
            homework = check_response(response)

            if not homework:
                logger.error('Список домашних работ пуст')
            else:
                homework = homework[0]
                message = parse_status(homework)
                if status_message != message:
                    status_message = message
                    send_message(bot, message)
                else:
                    logger.debug('Статус проверки работы не изменился')

            current_timestamp = current_timestamp

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if error_message != message:
                error_message = message
                send_message(bot, message)
                logger.info('Сообщение об ошибке отправлено в Телеграм')
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
