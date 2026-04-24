from __future__ import annotations

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException


class TwoFARequiredException(DomainException):
    """Требуется 2FA."""

    def __init__(self) -> None:
        super().__init__("Требуется двухфакторная аутентификация")


class InvalidTwoFACodeException(DomainException):
    """Неверный код 2FA."""

    def __init__(self) -> None:
        super().__init__("Неверный код двухфакторной аутентификации")


class OAuthProviderAlreadyLinkedException(BusinessRuleViolationException):
    """OAuth-провайдер уже привязан к аккаунту."""

    def __init__(self, provider: str) -> None:
        super().__init__(
            rule="UniqueOAuthProvider",
            message=f"Провайдер {provider} уже привязан",
        )
        self.provider = provider
