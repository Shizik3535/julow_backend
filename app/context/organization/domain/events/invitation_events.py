from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_domain_event import BaseDomainEvent


@dataclass(frozen=True)
class InvitationSent(BaseDomainEvent):
    """Приглашение отправлено."""

    org_id: str = ""
    email: str = ""
    role_id: str = ""


@dataclass(frozen=True)
class InvitationAccepted(BaseDomainEvent):
    """Приглашение принято."""

    org_id: str = ""
    user_id: str = ""


@dataclass(frozen=True)
class InvitationDeclined(BaseDomainEvent):
    """Приглашение отклонено."""

    org_id: str = ""
    email: str = ""


@dataclass(frozen=True)
class InvitationRevoked(BaseDomainEvent):
    """Приглашение отозвано."""

    org_id: str = ""
    invitation_id: str = ""


@dataclass(frozen=True)
class InvitationLinkGenerated(BaseDomainEvent):
    """Ссылка-приглашение сгенерирована."""

    org_id: str = ""
    token: str = ""
