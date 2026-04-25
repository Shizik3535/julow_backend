from __future__ import annotations

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class OrganizationNotFoundException(EntityNotFoundException):
    """Организация не найдена."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="Organization", id=id)


class OrganizationSuspendedException(DomainException):
    """Организация приостановлена."""

    def __init__(self) -> None:
        super().__init__("Организация приостановлена")


class OrganizationAlreadySuspendedException(BusinessRuleViolationException):
    """Организация уже приостановлена."""

    def __init__(self) -> None:
        super().__init__(
            rule="OrganizationAlreadySuspended",
            message="Организация уже приостановлена",
        )


class OrganizationAlreadyActiveException(BusinessRuleViolationException):
    """Организация уже активна."""

    def __init__(self) -> None:
        super().__init__(
            rule="OrganizationAlreadyActive",
            message="Организация уже активна",
        )


class OrganizationDeletionAlreadyRequestedException(BusinessRuleViolationException):
    """Запрос удаления организации уже отправлен."""

    def __init__(self) -> None:
        super().__init__(
            rule="OrganizationDeletionAlreadyRequested",
            message="Запрос удаления организации уже отправлен",
        )


class CannotRemoveOwnerException(BusinessRuleViolationException):
    """Нельзя удалить владельца из организации."""

    def __init__(self, user_id: str = "") -> None:
        super().__init__(
            rule="OwnerCannotBeRemoved",
            message=f"Нельзя удалить владельца из организации{f': {user_id}' if user_id else ''}",
        )


class CannotRemoveLastOwnerException(BusinessRuleViolationException):
    """Нельзя удалить последнего владельца."""

    def __init__(self) -> None:
        super().__init__(
            rule="AtLeastOneOwner",
            message="Нельзя удалить последнего владельца организации",
        )


class CannotTransferOwnershipException(BusinessRuleViolationException):
    """Нельзя передать владение."""

    def __init__(self, reason: str = "") -> None:
        msg = "Нельзя передать владение"
        if reason:
            msg += f": {reason}"
        super().__init__(
            rule="OwnershipTransfer",
            message=msg,
        )


class SecurityPolicyViolationException(DomainException):
    """Нарушение политики безопасности."""

    def __init__(self, detail: str = "") -> None:
        msg = "Нарушение политики безопасности"
        if detail:
            msg += f": {detail}"
        super().__init__(msg)


class SSOProviderAlreadyExistsException(BusinessRuleViolationException):
    """SSO-провайдер уже настроен."""

    def __init__(self, provider: str = "") -> None:
        super().__init__(
            rule="UniqueSSOProvider",
            message=f"SSO-провайдер {provider} уже настроен" if provider else "SSO-провайдер уже настроен",
        )


class StorageQuotaExceededException(BusinessRuleViolationException):
    """Квота хранилища превышена."""

    def __init__(self) -> None:
        super().__init__(
            rule="StorageQuota",
            message="Квота хранилища превышена",
        )
