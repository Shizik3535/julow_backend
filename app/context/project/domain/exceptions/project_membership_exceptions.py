from __future__ import annotations

from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class ProjectMemberNotFoundException(EntityNotFoundException):
    """Участник проекта не найден."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="ProjectMember", id=id)


class CannotRemoveOwnerAsMemberException(BusinessRuleViolationException):
    """Владелец не может быть удалён — сначала снимите роль."""

    def __init__(self, user_id: str = "") -> None:
        super().__init__(
            rule="OwnerCannotBeRemovedAsMember",
            message=f"Владелец не может быть удалён из участников{f': {user_id}' if user_id else ''}",
        )


class CannotRemoveLastOwnerException(BusinessRuleViolationException):
    """Нельзя удалить последнего владельца."""

    def __init__(self) -> None:
        super().__init__(
            rule="AtLeastOneOwner",
            message="Нельзя удалить последнего владельца проекта",
        )
