from __future__ import annotations

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class InvitationNotFoundException(EntityNotFoundException):
    """Приглашение не найдено."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="WorkspaceInvitation", id=id)


class InvitationExpiredException(DomainException):
    """Приглашение истекло."""

    def __init__(self) -> None:
        super().__init__("Приглашение истекло")


class InvitationLinkExpiredException(DomainException):
    """Ссылка-приглашение истекла."""

    def __init__(self) -> None:
        super().__init__("Ссылка-приглашение истекла")


class InvitationLinkMaxUsesExceededException(BusinessRuleViolationException):
    """Лимит использований ссылки-приглашения исчерпан."""

    def __init__(self) -> None:
        super().__init__(
            rule="InvitationLinkMaxUses",
            message="Лимит использований ссылки-приглашения исчерпан",
        )


class DuplicateInvitationException(BusinessRuleViolationException):
    """Приглашение уже отправлено."""

    def __init__(self, email: str = "") -> None:
        super().__init__(
            rule="UniqueInvitation",
            message=f"Приглашение уже отправлено{f': {email}' if email else ''}",
        )
