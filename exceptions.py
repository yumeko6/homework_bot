class EnvVariableError(Exception):
    """
    Выбрасывает исключение, если отсутствует хотя бы одна переменная окружения.
    """


class HomeworkStatusError(Exception):
    """
    Выбрасывает исключение, если в ответе API отсутствует ключ status.
    """
