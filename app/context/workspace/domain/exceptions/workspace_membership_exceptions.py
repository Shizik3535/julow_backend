from __future__ import annotations

from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class WorkspaceMemberNotFoundException(EntityNotFoundException):
    """Участник workspace не найден."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="WorkspaceMember", id=id)


class CannotRemoveOwnerAsMemberException(BusinessRuleViolationException):
    """Владелец не может быть удалён/деактивирован — сначала снимите роль владельца."""

    def __init__(self, user_id: str = "") -> None:
        super().__init__(
            rule="OwnerCannotBeRemovedAsMember",
            message=f"Владелец не может быть удалён из участников{f': {user_id}' if user_id else ''}",
        )


class MembershipLimitExceededException(BusinessRuleViolationException):
    """Лимит участников превышен."""

    def __init__(self, max_members: int = 0) -> None:
        super().__init__(
            rule="MaxMembers",
            message=f"Лимит участников превышен (максимум: {max_members})",
        )


class EmailDomainNotAllowedException(BusinessRuleViolationException):
    """Домен email не разрешён политикой."""

    def __init__(self, domain: str = "") -> None:
        super().__init__(
            rule="AllowedEmailDomains",
            message=f"Домен email не разрешён: {domain}" if domain else "Домен email не разрешён политикой",
        )
