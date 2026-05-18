from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_domain_event import BaseDomainEvent


@dataclass(frozen=True)
class ProjectInvitationSent(BaseDomainEvent):
    """
    Приглашение в проект отправлено по email.

    Атрибуты:
        invitation_id: ID агрегата ProjectInvitation. Нужен `OnProjectInvitationSentNotify`,
            чтобы передать его в `data.invitation_id` уведомления — фронт затем
            использует это значение, вызывая `POST /project-invitations/{id}/accept`.
        project_id: ID проекта.
        email: Адрес приглашаемого. Используется для lookup `get_user_by_email`,
            чтобы понять, есть ли уже пользователь в системе.
        role_id: ID роли проекта (для будущего; пока не выводим на UI).
        invited_by: ID пользователя-владельца, отправившего приглашение.
            Не используется в `OnProjectInvitationSentNotify`, но сохранён
            в payload ради консистентности контракта (event payload содержит
            всё необходимое для аудита).
    """

    invitation_id: str = ""
    project_id: str = ""
    email: str = ""
    role_id: str = ""
    invited_by: str = ""


@dataclass(frozen=True)
class ProjectInvitationLinkGenerated(BaseDomainEvent):
    """Ссылка-приглашение для проекта сгенерирована."""

    project_id: str = ""
    token: str = ""


@dataclass(frozen=True)
class ProjectInvitationAccepted(BaseDomainEvent):
    """
    Приглашение в проект принято.

    Атрибуты:
        invitation_id: ID агрегата (для аудита/корреляции).
        project_id: ID проекта.
        user_id: ID пользователя, принявшего приглашение.
        invited_by: ID пользователя, отправившего приглашение —
            именно ему `OnProjectInvitationAcceptedNotify` положит
            уведомление «X присоединился к проекту».
        email: Email принявшего (если приглашение было email-типа). Помогает
            inviter'у в UI понять «кто это» без отдельного запроса в Identity.
    """

    invitation_id: str = ""
    project_id: str = ""
    user_id: str = ""
    invited_by: str = ""
    email: str = ""


@dataclass(frozen=True)
class ProjectInvitationDeclined(BaseDomainEvent):
    """
    Приглашение в проект отклонено.

    Атрибуты:
        invitation_id: ID агрегата.
        project_id: ID проекта.
        email: Email приглашённого.
        invited_by: ID пользователя, отправившего приглашение — получатель
            уведомления «X отклонил приглашение».
        user_id: ID отклонившего (если был залогинен).
    """

    invitation_id: str = ""
    project_id: str = ""
    email: str = ""
    invited_by: str = ""
    user_id: str = ""


@dataclass(frozen=True)
class ProjectInvitationRevoked(BaseDomainEvent):
    """Приглашение в проект отозвано."""

    project_id: str = ""
    invitation_id: str = ""
