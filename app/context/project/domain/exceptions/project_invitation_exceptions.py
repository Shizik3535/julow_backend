from __future__ import annotations

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class ProjectInvitationNotFoundException(EntityNotFoundException):
    """Приглашение в проект не найдено."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="ProjectInvitation", id=id)


class ProjectInvitationExpiredException(DomainException):
    """Приглашение в проект истекло."""

    def __init__(self) -> None:
        super().__init__("Приглашение в проект истекло")


class ProjectInvitationLinkExpiredException(DomainException):
    """Ссылка-приглашение в проект истекла."""

    def __init__(self) -> None:
        super().__init__("Ссылка-приглашение в проект истекла")


class ProjectInvitationLinkMaxUsesExceededException(BusinessRuleViolationException):
    """Лимит использований ссылки-приглашения исчерпан."""

    def __init__(self) -> None:
        super().__init__(
            rule="ProjectInvitationLinkMaxUses",
            message="Лимит использований ссылки-приглашения исчерпан",
        )


class DuplicateProjectInvitationException(BusinessRuleViolationException):
    """Приглашение в проект уже отправлено."""

    def __init__(self, email: str = "") -> None:
        super().__init__(
            rule="UniqueProjectInvitation",
            message=f"Приглашение уже отправлено{f': {email}' if email else ''}",
        )
