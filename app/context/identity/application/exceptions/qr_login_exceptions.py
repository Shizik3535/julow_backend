from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class QrLoginNotFoundException(ApplicationException):
    http_status_code = 404
    error_code = "QR_LOGIN_NOT_FOUND"

    def __init__(self) -> None:
        super().__init__("QR-код не найден или уже использован")


class QrLoginExpiredException(ApplicationException):
    http_status_code = 410
    error_code = "QR_LOGIN_EXPIRED"

    def __init__(self) -> None:
        super().__init__("Срок действия QR-кода истёк")


class QrLoginInvalidStateException(ApplicationException):
    http_status_code = 409
    error_code = "QR_LOGIN_INVALID_STATE"

    def __init__(self, message: str = "QR-код уже подтверждён или недоступен") -> None:
        super().__init__(message)
