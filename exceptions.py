class EnvVariableError(Exception):
    def __str__(self):
        return 'Отсутствует переменная окружения!'


class HomeworkStatusError(Exception):
    def __str__(self):
        return 'В ответе API отсутствует ключ status'
