import requests


def send_request(url: str, timeout=10):
    """
    Отправить запрос по url

    Ключевые аргументы:
    url: адресс сервера на который отправить запрос
    timeout: время ожидания ответа от сервера в секундах (по умолчанию 10 секунд)

    Исключения:
    raise TimeoutExceeded: Превышено время ожидания ответа от сервера
    raise NetworkProblem: Проблемы с подключением к серверу

    return: объект response (ответ от сервера)
    """
    try:
        return requests.get(url, timeout=timeout)

    except requests.exceptions.Timeout:
        print('Ошибка подключения: Время ожидания ответа превысило 10 секунд.')

    except requests.exceptions.ConnectionError:
        print('Неполадки в сети: отказ от соединения')