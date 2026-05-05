from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class AuthenticationFailedException(ApplicationException):
    """Аутентификация не удалась (неверные учётные данные)."""

    http_status_code = 401
    error_code = "AUTHENTICATION_FAILED"

    def __init__(self) -> None:
        super().__init__("Неверный email или пароль")


class AccountLockedException(ApplicationException):
    """Аккаунт заблокирован после неудачных попыток входа."""

    http_status_code = 403
    error_code = "ACCOUNT_LOCKED"

    def __init__(self, locked_until: str | None = None) -> None:
        msg = "Аккаунт временно заблокирован"
        if locked_until:
            msg += f" до {locked_until}"
        super().__init__(msg)
        self.locked_until = locked_until


class TwoFARequiredAppException(ApplicationException):
    """Требуется двухфакторная аутентификация для завершения входа."""

    http_status_code = 403
    error_code = "TWO_FA_REQUIRED"

    def __init__(self) -> None:
        super().__init__("Требуется двухфакторная аутентификация")


class SSOEnforcedException(ApplicationException):
    """Вход через email+password запрещён — организация требует SSO."""

    http_status_code = 403
    error_code = "SSO_ENFORCED"

    def __init__(self) -> None:
        super().__init__("Вход возможен только через SSO")
