class EnvVariableError(Exception):
    def __str__(self):
        return 'Отсутствует переменная окружения!'


class ResponseStatusCodeError(Exception):
    def __str__(self):
        return 'API не отвечает на запрос'


class HomeworkStatusError(Exception):
    def __str__(self):
        return 'В ответе API отсутствует ключ status'
