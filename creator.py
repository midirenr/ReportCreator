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


def correlate_users_and_tasks(users: list[dict], tasks: list[dict]) -> None:
    """
    Установить соотношение между users и tasks

    Ключевые аргументы:
    users - список, каждый элемент которого является словарем с информацией о юзере
    tasks - список, каждый элемент которого является словарем с информацией о задаче.
    Каждая задача связана с юзером по ключу userId.

    Описание:
    - проходит циклом по каждому словарю в двух принятых в качестве аргумента списках;
    - создает новые пары ключ-значение в словаре из списка users:
    completed_task: словарь из списка tasks у которого completed=True
    uncompleted_task: словарь из списка tasks у которого completed=False
    - в случае совпадения user['id'] и task['userId'] добавляет task в user['completed_task'/'uncompleted_task']
    """
    for user in users:
        user['completed_task'] = []
        user['uncompleted_task'] = []
        for task in tasks:
            if user['id'] != task['userId']:
                continue
            if task['completed']:
                user['completed_task'].append(task)
            else:
                user['uncompleted_task'].append(task)
