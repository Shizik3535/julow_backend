from __future__ import annotations

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class UserNotFoundException(EntityNotFoundException):
    """Пользователь не найден."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="User", id=id)


class InvalidCredentialsException(DomainException):
    """Неверные учётные данные."""

    def __init__(self) -> None:
        super().__init__("Неверные учётные данные")


class UserBlockedException(DomainException):
    """Пользователь заблокирован."""

    def __init__(self, locked_until: str | None = None) -> None:
        msg = "Пользователь заблокирован"
        if locked_until:
            msg += f" до {locked_until}"
        super().__init__(msg)
        self.locked_until = locked_until


class EmailNotConfirmedException(DomainException):
    """Email не подтверждён."""

    def __init__(self) -> None:
        super().__init__("Email не подтверждён")


class InvalidVerificationTokenException(DomainException):
    """Неверный или просроченный токен верификации."""

    def __init__(self) -> None:
        super().__init__("Токен верификации недействителен или просрочен")


class AccountDeletionPendingException(DomainException):
    """Аккаунт в процессе удаления."""

    def __init__(self) -> None:
        super().__init__("Аккаунт в процессе удаления")


class AccountNotPendingDeletionException(BusinessRuleViolationException):
    """Аккаунт не в статусе pending_deletion — отменять нечего."""

    def __init__(self) -> None:
        super().__init__(
            rule="AccountMustBePendingDeletion",
            message="Аккаунт не в статусе ожидания удаления",
        )


class AccountNotDisabledException(BusinessRuleViolationException):
    """Аккаунт не в статусе disabled — реактивация невозможна."""

    def __init__(self) -> None:
        super().__init__(
            rule="AccountMustBeDisabled",
            message="Аккаунт не деактивирован",
        )


class RoleNotFoundException(EntityNotFoundException):
    """Роль не найдена."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="Role", id=id)


class DuplicateRoleException(BusinessRuleViolationException):
    """Роль уже назначена пользователю."""

    def __init__(self) -> None:
        super().__init__(
            rule="UniqueRoleAssignment",
            message="Роль уже назначена пользователю",
        )


class LastSystemRoleException(BusinessRuleViolationException):
    """Нельзя снять последнюю системную роль."""

    def __init__(self) -> None:
        super().__init__(
            rule="AtLeastOneSystemRole",
            message="Нельзя снять последнюю системную роль",
        )


class CannotUnlinkLastProviderException(BusinessRuleViolationException):
    """Нельзя отвязать последний метод входа."""

    def __init__(self) -> None:
        super().__init__(
            rule="MustHaveAtLeastOneAuthProvider",
            message="Нельзя отвязать последний метод входа",
        )


class InvalidBackupCodeException(DomainException):
    """Неверный или уже использованный резервный код."""

    def __init__(self) -> None:
        super().__init__("Неверный или использованный резервный код")
