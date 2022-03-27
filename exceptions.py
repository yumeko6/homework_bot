class EnvVariableError(Exception):
    def __str__(self):
        return 'Отсутствует переменная окружения!'


class ResponseStatusCodeError(Exception):
    def __str__(self):
        return 'API не отвечает на запрос'


class ApiResponseError(Exception):
    def __str__(self):
        return 'Ошибка в ответе API'


class HomeworkTypeError(Exception):
    def __str__(self):
        return 'Список домашних работ не является списком'


class HomeworkNameError(Exception):
    def __str__(self):
        return 'В ответе API отсутствует ключ homework_name'


class HomeworkStatusError(Exception):
    def __str__(self):
        return 'В ответе API отсутствует ключ status'


class ApiResponseTypeError(Exception):
    def __str__(self):
        return 'Ответ API не является словарем'


class TestError(Exception):
    def __str__(self):
        return '123'
