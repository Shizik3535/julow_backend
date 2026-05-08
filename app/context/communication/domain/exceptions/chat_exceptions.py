from __future__ import annotations

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class ChatNotFoundException(EntityNotFoundException):
    """Чат не найден."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="Chat", id=id)


class NotChatMemberException(DomainException):
    """Не участник чата."""

    def __init__(self) -> None:
        super().__init__("Не участник чата")


class ChatAlreadyExistsException(BusinessRuleViolationException):
    """DM между пользователями уже существует."""

    def __init__(self) -> None:
        super().__init__(
            rule="UniqueDM",
            message="DM между пользователями уже существует",
        )


class CannotAddMemberToDMException(BusinessRuleViolationException):
    """Нельзя добавить участника в DM."""

    def __init__(self) -> None:
        super().__init__(
            rule="DMFixedMembers",
            message="Нельзя добавить участника в DM",
        )


class CannotRemoveFromDMException(BusinessRuleViolationException):
    """Нельзя удалить участника из DM."""

    def __init__(self) -> None:
        super().__init__(
            rule="DMFixedMembers",
            message="Нельзя удалить участника из DM",
        )


class InvalidChatMemberRoleException(BusinessRuleViolationException):
    """Некорректная роль участника."""

    def __init__(self, detail: str = "") -> None:
        super().__init__(
            rule="ValidChatMemberRole",
            message=f"Некорректная роль участника{f': {detail}' if detail else ''}",
        )


class ThreadNotFoundException(EntityNotFoundException):
    """Тред не найден."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="Thread", id=id)


class ThreadAlreadyResolvedException(BusinessRuleViolationException):
    """Тред уже закрыт."""

    def __init__(self) -> None:
        super().__init__(
            rule="ThreadNotAlreadyResolved",
            message="Тред уже закрыт",
        )


class ChatArchivedException(DomainException):
    """Чат архивирован."""

    def __init__(self) -> None:
        super().__init__("Чат архивирован")


class CannotRemoveChatOwnerException(BusinessRuleViolationException):
    """Нельзя удалить владельца чата."""

    def __init__(self) -> None:
        super().__init__(
            rule="ChatOwnerCannotBeRemoved",
            message="Нельзя удалить владельца чата",
        )
