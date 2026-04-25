from __future__ import annotations

from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class OrgRoleNotFoundException(EntityNotFoundException):
    """Роль организации не найдена."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="OrgRole", id=id)


class OrgRoleInUseException(BusinessRuleViolationException):
    """Роль используется, нельзя удалить."""

    def __init__(self, role_name: str = "") -> None:
        super().__init__(
            rule="RoleInUse",
            message=f"Роль используется, нельзя удалить{f': {role_name}' if role_name else ''}",
        )


class CannotDeleteSystemRoleException(BusinessRuleViolationException):
    """Нельзя удалить системную роль."""

    def __init__(self, role_name: str = "") -> None:
        super().__init__(
            rule="SystemRoleCannotBeDeleted",
            message=f"Нельзя удалить системную роль{f': {role_name}' if role_name else ''}",
        )


class CannotUpdateSystemRoleException(BusinessRuleViolationException):
    """Нельзя обновить системную роль."""

    def __init__(self, role_name: str = "") -> None:
        super().__init__(
            rule="SystemRoleCannotBeUpdated",
            message=f"Нельзя обновить системную роль{f': {role_name}' if role_name else ''}",
        )
