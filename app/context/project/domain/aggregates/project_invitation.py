from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.events.project_invitation_events import (
    ProjectInvitationAccepted,
    ProjectInvitationDeclined,
    ProjectInvitationLinkGenerated,
    ProjectInvitationRevoked,
    ProjectInvitationSent,
)
from app.context.project.domain.exceptions.project_invitation_exceptions import (
    ProjectInvitationLinkExpiredException,
    ProjectInvitationLinkMaxUsesExceededException,
)
from app.context.project.domain.value_objects.invitation_status import InvitationStatus
from app.context.project.domain.value_objects.invitation_token import InvitationToken


@dataclass
class ProjectInvitation(AggregateRoot):
    """
    Корень агрегата приглашения в проект (Project BC).

    Два типа приглашений:
    - Email-приглашение (email заполнен, link=None)
    - Link-приглашение (link заполнен, email=None) — link также служит «кодом»

    Атрибуты:
        project_id: Opaque ID проекта.
        workspace_id: Opaque ID workspace (для удобства join'ов и ACL).
        email: Email для email-приглашений.
        link: Токен для link/code-приглашений.
        role_id: Opaque ID роли проекта.
        invited_by: ID пригласившего.
        invited_at: Время приглашения.
        status: Статус приглашения.
        user_id: ID пользователя, принявшего/отклонившего.
    """

    project_id: Id = field(default_factory=Id.generate)
    workspace_id: Id = field(default_factory=Id.generate)
    email: Email | None = None
    link: InvitationToken | None = None
    role_id: Id = field(default_factory=Id.generate)
    invited_by: Id = field(default_factory=Id.generate)
    invited_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    status: InvitationStatus = InvitationStatus.PENDING
    user_id: Id | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    # --- Фабричные методы ---

    @classmethod
    def create_email_invitation(
        cls,
        project_id: Id,
        workspace_id: Id,
        email: Email,
        role_id: Id,
        invited_by: Id,
    ) -> ProjectInvitation:
        """Создаёт email-приглашение."""
        invitation = cls(
            project_id=project_id,
            workspace_id=workspace_id,
            email=email,
            link=None,
            role_id=role_id,
            invited_by=invited_by,
        )
        invitation._register_event(
            ProjectInvitationSent(
                invitation_id=str(invitation.id),
                project_id=str(project_id),
                email=str(email),
                role_id=str(role_id),
                invited_by=str(invited_by),
            )
        )
        return invitation

    @classmethod
    def create_link_invitation(
        cls,
        project_id: Id,
        workspace_id: Id,
        role_id: Id,
        invited_by: Id,
        token_value: str,
        expires_at: datetime | None = None,
        max_uses: int | None = None,
    ) -> ProjectInvitation:
        """Создаёт link/code-приглашение."""
        token = InvitationToken(
            value=token_value,
            expires_at=expires_at,
            max_uses=max_uses,
            used_count=0,
        )
        invitation = cls(
            project_id=project_id,
            workspace_id=workspace_id,
            email=None,
            link=token,
            role_id=role_id,
            invited_by=invited_by,
        )
        invitation._register_event(
            ProjectInvitationLinkGenerated(
                project_id=str(project_id),
                token=token_value,
            )
        )
        return invitation

    # --- Инварианты ---

    def _assert_pending(self) -> None:
        if self.status != InvitationStatus.PENDING:
            raise ValueError(f"Приглашение не в статусе PENDING: {self.status.value}")

    # --- Бизнес-методы ---

    def accept(self, user_id: Id) -> None:
        """Принимает приглашение."""
        self._assert_pending()
        self.user_id = user_id
        self.status = InvitationStatus.ACCEPTED
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            ProjectInvitationAccepted(
                invitation_id=str(self.id),
                project_id=str(self.project_id),
                user_id=str(user_id),
                invited_by=str(self.invited_by),
                email=str(self.email) if self.email else "",
            )
        )

    def decline(self, user_id: Id | None = None) -> None:
        """Отклоняет приглашение."""
        self._assert_pending()
        self.user_id = user_id
        self.status = InvitationStatus.DECLINED
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            ProjectInvitationDeclined(
                invitation_id=str(self.id),
                project_id=str(self.project_id),
                email=str(self.email) if self.email else "",
                invited_by=str(self.invited_by),
                user_id=str(user_id) if user_id is not None else "",
            )
        )

    def revoke(self) -> None:
        """Отзывает приглашение."""
        self._assert_pending()
        self.status = InvitationStatus.REVOKED
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            ProjectInvitationRevoked(
                project_id=str(self.project_id),
                invitation_id=str(self.id),
            )
        )

    def increment_link_usage(self) -> None:
        """Увеличивает счётчик использований ссылки/кода."""
        if self.link is None:
            return
        if self.link.is_expired:
            raise ProjectInvitationLinkExpiredException()
        if self.link.is_max_uses_exceeded:
            raise ProjectInvitationLinkMaxUsesExceededException()
        new_token = InvitationToken(
            value=self.link.value,
            expires_at=self.link.expires_at,
            max_uses=self.link.max_uses,
            used_count=self.link.used_count + 1,
        )
        self.link = new_token
        self.updated_at = datetime.now(tz=timezone.utc)

    def expire_if_needed(self) -> None:
        """Помечает приглашение как истёкшее, если время вышло."""
        if self.status != InvitationStatus.PENDING:
            return
        if self.email is not None:
            return
        if self.link is not None and self.link.is_expired:
            self.status = InvitationStatus.EXPIRED
            self.updated_at = datetime.now(tz=timezone.utc)
