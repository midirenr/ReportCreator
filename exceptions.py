class ReportCreatorBaseException(Exception):
    """
    Базовое исключение программы
    """
    def __init__(self, message='Было вызвано исключение ReportCreatorBaseException'):
        self.message = message

    def __str__(self):
        return self.message


class IncorrectResponseException(ReportCreatorBaseException):
    """
    Ислючение для функций:
    clearing_data_from_users_api
    clearing_data_from_todos_api

    Возникает в случае передачи функции некорректного response
    """
    def __init__(self, message='Было вызвано исключение IncorrectResponse'):
        self.message = message


class NetworkProblemException(ReportCreatorBaseException):
    """
    Исключение для функции send_request

    Возникает в случае проблем с подключением к API
    """
    def __init__(self, message='Было вызвано исключение NetworkProblemException'):
        self.message = message


class TimeoutExceededException(ReportCreatorBaseException):
    """
    Исключение для функции send_request

    Возникает в случае превышения времени ожидания ответа от API
    """
    def __init__(self, message='Было вызвано исключение TimeoutExceededException'):
        self.message = message
