from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class DeviceTokenAlreadyExistsException(ApplicationException):
    """Токен устройства уже зарегистрирован."""

    http_status_code = 409
    error_code = "DEVICE_TOKEN_ALREADY_EXISTS"

    def __init__(self, token: str) -> None:
        super().__init__(f"Токен устройства уже зарегистрирован: {token}")
        self.token = token


class DuplicateNotificationException(ApplicationException):
    """Дубликат уведомления (по group_key)."""

    http_status_code = 409
    error_code = "DUPLICATE_NOTIFICATION"

    def __init__(self, group_key: str = "") -> None:
        super().__init__(f"Уведомление с таким ключом группировки уже существует: {group_key}")
        self.group_key = group_key
