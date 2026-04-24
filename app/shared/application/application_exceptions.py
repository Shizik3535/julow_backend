from __future__ import annotations


class ApplicationException(Exception):
    """
    Базовое исключение application-слоя.

    Все специфичные исключения application-слоя должны наследоваться
    от этого класса. Позволяет отличать ошибки приложения
    от доменных и инфраструктурных на верхних уровнях.

    Атрибуты:
        message: Человекочитаемое описание ошибки.
        http_status_code: HTTP-код ответа (по умолчанию 400).
        error_code: Машиночитаемый код ошибки.

    Пример:
        class InvalidTokenException(ApplicationException):
            http_status_code = 401
            error_code = "INVALID_TOKEN"

            def __init__(self, detail: str = "Invalid or expired token") -> None:
                super().__init__(detail)
    """

    http_status_code: int = 400
    error_code: str = "APPLICATION_ERROR"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
