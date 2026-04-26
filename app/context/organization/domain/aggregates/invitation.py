from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.value_objects.invitation_status import InvitationStatus
from app.context.organization.domain.value_objects.invitation_token import InvitationToken
from app.context.organization.domain.events.invitation_events import (
    InvitationSent,
    InvitationAccepted,
    InvitationDeclined,
    InvitationRevoked,
    InvitationLinkGenerated,
)
from app.context.organization.domain.exceptions.invitation_exceptions import (
    InvitationExpiredException,
    InvitationLinkExpiredException,
    InvitationLinkMaxUsesExceededException,
)


@dataclass
class Invitation(AggregateRoot):
    """
    Корень агрегата приглашения (Organization BC).

    Два типа приглашений:
    - Email-приглашение (email заполнен, link=None)
    - Link-приглашение (link заполнен, email=None)

    Атрибуты:
        org_id: Opaque ID организации.
        email: Email для email-приглашений.
        link: Токен для link-приглашений.
        role_id: Opaque ID роли (ссылка на OrgRole AR).
        invited_by: ID пригласившего.
        invited_at: Время приглашения.
        status: Статус приглашения.
        approved_by: ID подтвердившего (для require_approval).
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    org_id: Id = field(default_factory=Id.generate)
    email: Email | None = None
    link: InvitationToken | None = None
    role_id: Id = field(default_factory=Id.generate)
    invited_by: Id = field(default_factory=Id.generate)
    invited_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    status: InvitationStatus = InvitationStatus.PENDING
    approved_by: Id | None = None
    user_id: Id | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    # --- Фабричные методы ---

    @classmethod
    def create_email_invitation(
        cls,
        org_id: Id,
        email: Email,
        role_id: Id,
        invited_by: Id,
    ) -> Invitation:
        """Создаёт email-приглашение."""
        invitation = cls(
            org_id=org_id,
            email=email,
            link=None,
            role_id=role_id,
            invited_by=invited_by,
        )
        invitation._register_event(
            InvitationSent(
                org_id=str(org_id),
                email=str(email),
                role_id=str(role_id),
            )
        )
        return invitation

    @classmethod
    def create_link_invitation(
        cls,
        org_id: Id,
        role_id: Id,
        invited_by: Id,
        token_value: str,
        expires_at: datetime | None = None,
        max_uses: int | None = None,
    ) -> Invitation:
        """Создаёт link-приглашение."""
        token = InvitationToken(
            value=token_value,
            expires_at=expires_at,
            max_uses=max_uses,
            used_count=0,
        )
        invitation = cls(
            org_id=org_id,
            email=None,
            link=token,
            role_id=role_id,
            invited_by=invited_by,
        )
        invitation._register_event(
            InvitationLinkGenerated(
                org_id=str(org_id),
                token=token_value,
            )
        )
        return invitation

    # --- Инварианты ---

    def _assert_pending(self) -> None:
        """Проверяет, что приглашение в статусе PENDING."""
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
            InvitationAccepted(org_id=str(self.org_id), user_id=str(user_id))
        )

    def decline(self, user_id: Id | None = None) -> None:
        """Отклоняет приглашение."""
        self._assert_pending()
        self.user_id = user_id
        self.status = InvitationStatus.DECLINED
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            InvitationDeclined(
                org_id=str(self.org_id),
                email=str(self.email) if self.email else "",
            )
        )

    def revoke(self) -> None:
        """Отзывает приглашение."""
        self._assert_pending()
        self.status = InvitationStatus.REVOKED
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            InvitationRevoked(
                org_id=str(self.org_id),
                invitation_id=str(self.id),
            )
        )

    def increment_link_usage(self) -> None:
        """Увеличивает счётчик использований ссылки-приглашения."""
        if self.link is None:
            return
        if self.link.is_expired:
            raise InvitationLinkExpiredException()
        if self.link.is_max_uses_exceeded:
            raise InvitationLinkMaxUsesExceededException()
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
            # Email-приглашения истекают по общему таймауту (проверка на app-слое)
            return
        if self.link is not None and self.link.is_expired:
            self.status = InvitationStatus.EXPIRED
            self.updated_at = datetime.now(tz=timezone.utc)
