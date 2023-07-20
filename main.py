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
    - проходит циклом по каждому словарю в двух принятых в качестве аргумента списках, где:
        1) создает новые пары ключ-значение в словаре из списка users:
        completed_task: словарь из списка tasks у которого completed=True
        uncompleted_task: словарь из списка tasks у которого completed=False
        2) в случае совпадения user['id'] и task['userId'] добавляет task в user['completed_task'/'uncompleted_task']
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


def create_report(data_list: list[dict]) -> None:
    """
    Создать отчет

    Ключевые аргументы:
    data_list - список, каждый элемент которого является словарем с информацией о юзере и его тасках

    Описание:
    - создает директорию tasks, если не находит ее;
    - проходит циклом по каждому словарю в списке, где:
        1) подготавливает данные к записи в файл (функция create_write_data)
        2) получает из подготовленных данных дату и время формирования отчета (функция get_date_time_from_data)
        3) ищет уже существующий отчет по username юзера:
            3.1) в случае нахождения отчета:
                3.1.1) сравнивает новые данные с данными существующего отчета;
                3.1.2) если данные совпадают, то переходит к новой итерации;
                3.1.3) если не совпадают, то переименовывает старый отчет и создает новый.
            3.2) в случае отсутствия отчета создает новый
    """
    if not os.path.isdir('tasks'):
        os.mkdir('tasks')

    for data in data_list:
        write_data = create_data_to_write(data)
        date_time_of_write_data = get_date_time_from_data(write_data)

        if os.path.exists(f'tasks/{data["username"]}.txt'):
            file = open(f'tasks/{data["username"]}.txt', 'r')
            file_data = file.read()
            date_time_of_file_data = get_date_time_from_data(file_data)
            file.close()

            if write_data.replace(date_time_of_write_data, '') == file_data.replace(date_time_of_file_data, ''):
                continue
            else:
                rename_old_report(f'{data["username"]}.txt', date_time_of_file_data)
                new_file = open(f'tasks/{data["username"]}.txt', 'w')
                new_file.write(write_data)
                new_file.close()
        else:
            new_file = open(f'tasks/{data["username"]}.txt', 'w')
            new_file.write(write_data)
            new_file.close()


if __name__ == "__main__":
    # Отправляем запросы в API
    response_tasks = send_request('https://json.medrocket.ru/todos')
    response_users = send_request('https://json.medrocket.ru/users')

    # Проверяем корректно ли выполнен запрос
    if validate_response(response_users) and validate_response(response_tasks):
        # Очищаем полученные данные
        clearing_data_tasks = clearing_data_from_todos_api(response_tasks)
        clearing_data_users = clearing_data_from_users_api(response_users)
        # Устанавливаем соотношение между users и tasks
        correlate_users_and_tasks(clearing_data_users, clearing_data_tasks)
        # Создаем отчет
        create_report(clearing_data_users)
