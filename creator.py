import requests


def send_request(url: str, timeout=10):
    """
    Функция принимает обязательный аргумент:
    url - адрес на который будет отправлен GET запрос,
    и необязательный аргумент (по умолчанию 10 секунд):
    timeout - время ожидания ответа от сервера

    Вызывает исключение в случаях, когда не удалось подключиться к серверу или по timeout

    Возвращает response
    """
    try:
        return requests.get(url, timeout=timeout)

    except requests.exceptions.Timeout:
        print('Ошибка подключения: Время ожидания ответа превысило 10 секунд.')

    except requests.exceptions.ConnectionError:
        print('Неполадки в сети: отказ от соединения')