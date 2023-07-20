from datetime import datetime
import os
import re
from sys import platform


def create_data_to_write(data: dict) -> str:
    """
    Сгенерировать данные для записи в отчет

    Ключевые аргументы:
    data_list - словарь с информацией о юзере и его тасках
    """
    now_date_time = datetime.now()
    actual_task_title = ''
    finished_task_title = ''

    for task in data['uncompleted_task']:
        if len(task["title"]) > 46:
            task["title"] = task["title"][0:46] + '...'
        actual_task_title = actual_task_title + f'\n- {task["title"]}'

    for task in data['completed_task']:
        if len(task["title"]) > 46:
            task["title"] = task["title"][0:46] + '...'
        finished_task_title = finished_task_title + f'\n- {task["title"]}'

    if len(data['uncompleted_task']) == 0:
        actual_task_title = 'Актуальные задачи отсутствуют'

    if len(data['completed_task']) == 0:
        finished_task_title = 'Завершенные задачи отсутствуют'

    write_data = \
        f"# Отчёт для {data['company']['name']}.\n" \
        f"{data['name']} <{data['email']}> {now_date_time.strftime('%d.%m.%Y %H:%M')}\n" \
        f"Всего задач: {len(data['completed_task']) + len(data['uncompleted_task'])}\n" \
        f"\n" \
        f"## Актуальные задачи ({len(data['uncompleted_task'])}):\n" \
        f"{actual_task_title.strip()}\n" \
        f"\n" \
        f"## Завершённые задачи ({len(data['completed_task'])}):\n" \
        f"{finished_task_title.strip()}"

    return write_data


def get_date_time_from_data(data: str) -> str:
    """
    Получить дату и время из переданных данных
    """
    return re.search(r"\d\d\.\d\d\.\d\d\d\d \d\d:\d\d", data).group(0)


def rename_old_report(old_report_filename, date_time_of_old_report):
    """
    Переименовать старый отчет

    Описание:
    В зависимости от платформы, на которой будет запущенна программа, окончательное имя старого отчета будет отличаться.
    Windows OS не поддерживает ":" в имени файла.
    """
    if 'win' in platform:
        date_time_of_old_report = date_time_of_old_report.replace(".", "-").replace(" ", "T").replace(":", "-")
        os.rename(f'tasks/{old_report_filename}', f'tasks/old_{old_report_filename}_{date_time_of_old_report}.txt')
    else:
        date_time_of_old_report = date_time_of_old_report.replace(".", "-").replace(" ", "T")
        os.rename(f'tasks/{old_report_filename}', f'tasks/old_{old_report_filename}_{date_time_of_old_report}.txt')
