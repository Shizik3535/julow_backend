"""Unit-тесты для агрегата WorkspaceInvitation (Workspace BC)."""

from datetime import datetime, timedelta, timezone

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.aggregates.workspace_invitation import WorkspaceInvitation
from app.context.workspace.domain.value_objects.invitation_status import InvitationStatus
from app.context.workspace.domain.value_objects.invitation_token import InvitationToken
from app.context.workspace.domain.events.workspace_invitation_events import (
    InvitationSent,
    InvitationAccepted,
    InvitationDeclined,
    InvitationRevoked,
    InvitationLinkGenerated,
)
from app.context.workspace.domain.exceptions.workspace_invitation_exceptions import (
    InvitationLinkExpiredException,
    InvitationLinkMaxUsesExceededException,
)
from tests.factories import IdFactory


# ═══════════════════════════════════════════════════════════════════════════
# Создание email-приглашения
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEmailInvitationCreation:
    def test_create_email_invitation(self, email_invitation: WorkspaceInvitation, any_email: object) -> None:
        assert email_invitation.email == any_email
        assert email_invitation.link is None
        assert email_invitation.status == InvitationStatus.PENDING

    def test_create_email_invitation_emits_sent(self, email_invitation: WorkspaceInvitation) -> None:
        events = email_invitation.clear_domain_events()
        assert any(isinstance(e, InvitationSent) for e in events)

    def test_create_email_invitation_has_no_link(self, email_invitation: WorkspaceInvitation) -> None:
        assert email_invitation.link is None


# ═══════════════════════════════════════════════════════════════════════════
# Создание link-приглашения
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestLinkInvitationCreation:
    def test_create_link_invitation(self, link_invitation: WorkspaceInvitation) -> None:
        assert link_invitation.email is None
        assert link_invitation.link is not None
        assert link_invitation.link.value == "abc123"
        assert link_invitation.status == InvitationStatus.PENDING

    def test_create_link_invitation_emits_link_generated(self, link_invitation: WorkspaceInvitation) -> None:
        events = link_invitation.clear_domain_events()
        assert any(isinstance(e, InvitationLinkGenerated) for e in events)

    def test_create_link_invitation_has_no_email(self, link_invitation: WorkspaceInvitation) -> None:
        assert link_invitation.email is None


# ═══════════════════════════════════════════════════════════════════════════
# Принятие приглашения
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestInvitationAccept:
    def test_accept_pending_invitation(self, email_invitation: WorkspaceInvitation) -> None:
        user_id = IdFactory()
        email_invitation.accept(user_id)
        assert email_invitation.status == InvitationStatus.ACCEPTED

    def test_accept_emits_accepted(self, email_invitation: WorkspaceInvitation) -> None:
        user_id = IdFactory()
        email_invitation.accept(user_id)
        events = email_invitation.clear_domain_events()
        assert any(isinstance(e, InvitationAccepted) for e in events)

    def test_accept_non_pending_raises(self, email_invitation: WorkspaceInvitation) -> None:
        user_id = IdFactory()
        email_invitation.accept(user_id)
        with pytest.raises(ValueError):
            email_invitation.accept(IdFactory())


# ═══════════════════════════════════════════════════════════════════════════
# Отклонение приглашения
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestInvitationDecline:
    def test_decline_pending_invitation(self, email_invitation: WorkspaceInvitation) -> None:
        email_invitation.decline()
        assert email_invitation.status == InvitationStatus.DECLINED

    def test_decline_emits_declined(self, email_invitation: WorkspaceInvitation) -> None:
        email_invitation.decline()
        events = email_invitation.clear_domain_events()
        assert any(isinstance(e, InvitationDeclined) for e in events)

    def test_decline_non_pending_raises(self, email_invitation: WorkspaceInvitation) -> None:
        email_invitation.decline()
        with pytest.raises(ValueError):
            email_invitation.decline()


# ═══════════════════════════════════════════════════════════════════════════
# Отзыв приглашения
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestInvitationRevoke:
    def test_revoke_pending_invitation(self, email_invitation: WorkspaceInvitation) -> None:
        email_invitation.revoke()
        assert email_invitation.status == InvitationStatus.REVOKED

    def test_revoke_emits_revoked(self, email_invitation: WorkspaceInvitation) -> None:
        email_invitation.revoke()
        events = email_invitation.clear_domain_events()
        assert any(isinstance(e, InvitationRevoked) for e in events)

    def test_revoke_non_pending_raises(self, email_invitation: WorkspaceInvitation) -> None:
        email_invitation.revoke()
        with pytest.raises(ValueError):
            email_invitation.revoke()


# ═══════════════════════════════════════════════════════════════════════════
# Использование ссылки-приглашения
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestInvitationLinkUsage:
    def test_increment_link_usage(self, link_invitation: WorkspaceInvitation) -> None:
        link_invitation.increment_link_usage()
        assert link_invitation.link is not None
        assert link_invitation.link.used_count == 1

    def test_increment_expired_link_raises(self, any_workspace_id: Id, any_role_id: Id, any_owner_id: Id) -> None:
        past = datetime.now(tz=timezone.utc) - timedelta(hours=1)
        token = InvitationToken(value="expired", expires_at=past)
        inv = WorkspaceInvitation(
            workspace_id=any_workspace_id,
            link=token,
            role_id=any_role_id,
            invited_by=any_owner_id,
        )
        with pytest.raises(InvitationLinkExpiredException):
            inv.increment_link_usage()

    def test_increment_max_uses_exceeded_raises(self, any_workspace_id: Id, any_role_id: Id, any_owner_id: Id) -> None:
        token = InvitationToken(value="limited", max_uses=1, used_count=1)
        inv = WorkspaceInvitation(
            workspace_id=any_workspace_id,
            link=token,
            role_id=any_role_id,
            invited_by=any_owner_id,
        )
        with pytest.raises(InvitationLinkMaxUsesExceededException):
            inv.increment_link_usage()

    def test_increment_email_invitation_is_noop(self, email_invitation: WorkspaceInvitation) -> None:
        email_invitation.increment_link_usage()
        assert email_invitation.link is None


# ═══════════════════════════════════════════════════════════════════════════
# Истечение приглашения
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestInvitationExpiry:
    def test_expire_if_needed_pending_link_expired(
        self, any_workspace_id: Id, any_role_id: Id, any_owner_id: Id
    ) -> None:
        past = datetime.now(tz=timezone.utc) - timedelta(hours=1)
        token = InvitationToken(value="expired", expires_at=past)
        inv = WorkspaceInvitation(
            workspace_id=any_workspace_id,
            link=token,
            role_id=any_role_id,
            invited_by=any_owner_id,
        )
        inv.expire_if_needed()
        assert inv.status == InvitationStatus.EXPIRED

    def test_expire_if_needed_email_invitation_noop(self, email_invitation: WorkspaceInvitation) -> None:
        email_invitation.expire_if_needed()
        assert email_invitation.status == InvitationStatus.PENDING

    def test_expire_if_needed_non_pending_noop(
        self, any_workspace_id: Id, any_role_id: Id, any_owner_id: Id
    ) -> None:
        past = datetime.now(tz=timezone.utc) - timedelta(hours=1)
        token = InvitationToken(value="expired", expires_at=past)
        inv = WorkspaceInvitation(
            workspace_id=any_workspace_id,
            link=token,
            role_id=any_role_id,
            invited_by=any_owner_id,
            status=InvitationStatus.ACCEPTED,
        )
        inv.expire_if_needed()
        assert inv.status == InvitationStatus.ACCEPTED

    def test_expire_if_needed_link_not_expired(self, link_invitation: WorkspaceInvitation) -> None:
        link_invitation.expire_if_needed()
        assert link_invitation.status == InvitationStatus.PENDING
