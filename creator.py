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
        raise TimeoutExceeded(f'Превышено время ожидания ответа от сервера {url}, более {timeout} секунд')

    except requests.exceptions.ConnectionError:
        raise NetworkProblem(f'Не удалось подключиться к серверу {url}')


def validate_response(response) -> bool:
    """
    Проверить response на status_code=200 и application/json в Content-Type

    Ключевые аргументы:
    response: объект response (ответ от сервера)

    return:
    True: в случае прохождение проверки
    False: в провала проверки
    """
    if response.status_code == requests.codes.ok and 'application/json' in response.headers['Content-Type']:
        return True
    else:
        return False
