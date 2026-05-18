from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_domain_event import BaseDomainEvent


@dataclass(frozen=True)
class InvitationSent(BaseDomainEvent):
    """Приглашение отправлено.

    Атрибуты:
        invitation_id: ID агрегата WorkspaceInvitation. Нужен
            `OnWorkspaceInvitationSentNotify`, чтобы передать его в
            `data.invitation_id` уведомления — фронт вызывает
            `POST /invitations/{id}/accept|decline`.
        workspace_id: ID workspace.
        email: Email приглашаемого.
        role_id: ID роли.
        invited_by: ID отправителя приглашения.
    """

    invitation_id: str = ""
    workspace_id: str = ""
    email: str = ""
    role_id: str = ""
    invited_by: str = ""


@dataclass(frozen=True)
class InvitationAccepted(BaseDomainEvent):
    """Приглашение принято."""

    workspace_id: str = ""
    user_id: str = ""


@dataclass(frozen=True)
class InvitationDeclined(BaseDomainEvent):
    """Приглашение отклонено."""

    workspace_id: str = ""
    email: str = ""


@dataclass(frozen=True)
class InvitationRevoked(BaseDomainEvent):
    """Приглашение отозвано."""

    workspace_id: str = ""
    invitation_id: str = ""


@dataclass(frozen=True)
class InvitationLinkGenerated(BaseDomainEvent):
    """Ссылка-приглашение сгенерирована."""

    workspace_id: str = ""
    token: str = ""
