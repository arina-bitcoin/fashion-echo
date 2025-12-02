# Backend/app/core/exceptions.py

class FashionEchoException(Exception):
    """
    Базовое доменное исключение для проекта.
    Все наши "осмысленные" ошибки наследуем от него.
    """
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code


class NotFoundException(FashionEchoException):
    def __init__(self, resource: str):
        super().__init__(f"{resource} not found", "NOT_FOUND")


class ValidationException(FashionEchoException):
    def __init__(self, details: str):
        super().__init__(f"Validation error: {details}", "VALIDATION_ERROR")
