import os

import requests

from utils import create_data_to_write, get_date_time_from_data, rename_old_report
from exceptions import IncorrectResponseException, NetworkProblemException, TimeoutExceededException


def send_request(url: str, timeout=10.0):
    """
    Отправить запрос по url

    Ключевые аргументы:
    url: адрес сервера на который отправить запрос
    timeout: время ожидания ответа от сервера в секундах (по умолчанию 10 секунд)

    Исключения:
    raise TimeoutExceeded: Превышено время ожидания ответа от сервера
    raise NetworkProblem: Проблемы с подключением к серверу

    return: объект response (ответ от сервера)
    """
    try:
        return requests.get(url, timeout=timeout)
    except requests.exceptions.Timeout:
        raise TimeoutExceededException(f'Превышено время ожидания ответа от сервера {url}, более {timeout} секунд')
    except requests.exceptions.ConnectionError:
        raise NetworkProblemException(f'Не удалось подключиться к серверу {url}')


def validate_response(response) -> bool:
    """
    Проверить response на status_code=200 и application/json в Content-Type

    Ключевые аргументы:
    response: объект response (ответ от сервера)

    return:
    True: в случае прохождение проверки
    False: в случае провала проверки
    """
    if response.status_code == requests.codes.ok and 'application/json' in response.headers['Content-Type']:
        return True
    else:
        return False


def clearing_data_from_todos_api(response) -> list[dict]:
    """
    Очистить от некорректных данных полученных от todos API

    Ключевые аргументы:
    response: объект response (ответ от сервера)

    Цель:
    Отфильтровать данные полученные от API

    Описание:
    - Получает данные из response;
    - Проходит циклом по списку словарей полученному из response, где:
        1) Проверяет наличие данных необходимых для формирования отчета и их тип данных
        2) Добавляет валидные словари в список

    return: список очищенных словарей
    """
    if response.url != 'https://json.medrocket.ru/todos':
        raise IncorrectResponseException(f'Функция validate_data_from_todos_api '
                                         f'ожидала получить ответ от https://json.medrocket.ru/todos, '
                                         f'но получила от {response.url}')

    list_of_tasks = response.json()
    validated_data_list = []

    for task in list_of_tasks:
        if 'userId' not in task.keys() or type(task['userId']) != int:
            continue

        if 'id' not in task.keys() or type(task['id']) != int:
            continue

        if 'title' not in task.keys() or type(task['title']) != str:
            continue

        if 'completed' not in task.keys() or type(task['completed']) != bool:
            continue

        validated_data_list.append(task)

    return validated_data_list


def clearing_data_from_users_api(response) -> list[dict]:
    """
    Очистить от некорректных данных полученных от users API

    Ключевые аргументы:
    response: объект response (ответ от сервера)

    Цель:
    Отфильтровать данные полученные от API

    Описание:
    - Получает данные из response;
    - Проходит циклом по списку словарей полученному из response, где:
        1) Проверяет наличие данных необходимых для формирования отчета и их тип данных
        2) Добавляет валидные словари в список

    return: список очищенных словарей
    """
    if response.url != 'https://json.medrocket.ru/users':
        raise IncorrectResponseException(f'Функция validate_data_from_users_api '
                                         f'ожидала получить ответ от https://json.medrocket.ru/users, '
                                         f'но получила от {response.url}')

    list_of_users = response.json()
    validated_data_list = []

    for task in list_of_users:
        if 'name' not in task.keys() or type(task['name']) != str:
            continue

        if 'email' not in task.keys() or type(task['email']) != str:
            continue

        if 'username' not in task.keys() or type(task['username']) != str:
            continue

        if 'company' not in task.keys() or type(task['company']) != dict:
            continue

        if 'name' not in task['company'].keys() or type(task['company']['name']) != str:
            continue

        validated_data_list.append(task)

    return validated_data_list


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
