import http
import logging
import os
import sys
import time

import requests
import telegram
from dotenv import load_dotenv
from telegram import TelegramError

from exceptions import EnvVariableError, HomeworkStatusError


load_dotenv()

PRACTICUM_TOKEN = os.getenv('pr_token')
TELEGRAM_TOKEN = os.getenv('tel_token')
TELEGRAM_CHAT_ID = os.getenv('tel_chat_id')


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
        logging.info('Сообщение отправлено в Телеграм')
    except telegram.error.TelegramError as error:
        logging.error(f'Ошибка отправки сообщения в телеграм: {error}')
        raise TelegramError(f'Ошибка отправки сообщения в телеграм: {error}')
    except Exception as error:
        raise Exception(f'Непредвиденная ошибка: {error}')

    return message_sent


def get_api_answer(current_timestamp):
    """Получаем ответ от API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception as error:
        logging.error(f'Ошибка доступа к сайту: {error}')
        raise ConnectionError('Ошибка доступа к сайту') from error
    else:
        if response.status_code == http.HTTPStatus.OK:
            logging.info('Отправлен API запрос')
            response = response.json()
        else:
            logging.error('API не отвечает на запрос')
            raise ConnectionError('API не отвечает на запрос')

    return response


def check_response(response):
    """Проверяем ответ от API."""
    if not isinstance(response, dict):
        logging.error('Ответ API не является словарем')
        raise TypeError('Ответ API не является словарем')
    elif not isinstance(response.get('homeworks'), list):
        logging.error('Список домашних работ не является списком')
        raise TypeError('Список домашних работ не является списком')
    else:
        homeworks = response.get('homeworks')

    return homeworks


def parse_status(homework):
    """Получаем данные о домашней работе."""
    if homework.get('homework_name') is None:
        logging.error('В ответе API отсутствет ключ homework_name')
    homework_name = homework.get('homework_name')

    if homework.get('status') is None:
        logging.error('В ответе API отсутствует ключ status')
        raise HomeworkStatusError('В ответе API отсутствует ключ status')
    homework_status = homework.get('status')

    if homework.get('status') not in HOMEWORK_STATUSES:
        logging.error('Недокументированный статус работы')

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
                logging.critical('Отсутствует переменная окружения!')
                raise EnvVariableError('Отсутствует переменная окружения!')

            response = get_api_answer(current_timestamp)
            homework = check_response(response)

            if not homework:
                logging.error('Список домашних работ пуст')
            else:
                homework = homework[0]
                message = parse_status(homework)
                if status_message != message:
                    status_message = message
                    send_message(bot, message)
                else:
                    logging.debug('Статус проверки работы не изменился')

            current_timestamp = current_timestamp

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if error_message != message:
                error_message = message
                send_message(bot, message)
                logging.info('Сообщение об ошибке отправлено в Телеграм')
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s - %(name)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    main()
