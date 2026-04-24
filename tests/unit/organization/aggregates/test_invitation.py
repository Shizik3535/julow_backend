"""Unit-тесты для агрегата Invitation (Organization BC)."""

from datetime import datetime, timedelta, timezone

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.aggregates.invitation import Invitation
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
    InvitationLinkExpiredException,
    InvitationLinkMaxUsesExceededException,
)
from tests.factories import IdFactory


# ═══════════════════════════════════════════════════════════════════════════
# Email-приглашение
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEmailInvitationCreation:
    def test_create_email_invitation(self, email_invitation: Invitation) -> None:
        assert email_invitation.email is not None
        assert email_invitation.link is None
        assert email_invitation.status == InvitationStatus.PENDING

    def test_create_email_invitation_emits_invitation_sent(self, email_invitation: Invitation) -> None:
        events = email_invitation.clear_domain_events()
        assert any(isinstance(e, InvitationSent) for e in events)

    def test_create_email_invitation_has_pending_status(self, email_invitation: Invitation) -> None:
        assert email_invitation.status == InvitationStatus.PENDING


# ═══════════════════════════════════════════════════════════════════════════
# Link-приглашение
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestLinkInvitationCreation:
    def test_create_link_invitation(self, link_invitation: Invitation) -> None:
        assert link_invitation.email is None
        assert link_invitation.link is not None
        assert link_invitation.link.value == "abc123"

    def test_create_link_invitation_emits_link_generated(self, link_invitation: Invitation) -> None:
        events = link_invitation.clear_domain_events()
        assert any(isinstance(e, InvitationLinkGenerated) for e in events)

    def test_create_link_invitation_with_max_uses(self, any_org_id: Id, any_role_id: Id, any_owner_id: Id) -> None:
        inv = Invitation.create_link_invitation(
            org_id=any_org_id, role_id=any_role_id, invited_by=any_owner_id,
            token_value="xyz", max_uses=5,
        )
        assert inv.link is not None
        assert inv.link.max_uses == 5


# ═══════════════════════════════════════════════════════════════════════════
# Принятие
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestInvitationAccept:
    def test_accept(self, email_invitation: Invitation) -> None:
        user_id = IdFactory()
        email_invitation.accept(user_id)
        assert email_invitation.status == InvitationStatus.ACCEPTED

    def test_accept_emits_event(self, email_invitation: Invitation) -> None:
        user_id = IdFactory()
        email_invitation.accept(user_id)
        events = email_invitation.clear_domain_events()
        assert any(isinstance(e, InvitationAccepted) for e in events)

    def test_accept_non_pending_raises(self, accepted_invitation: Invitation) -> None:
        with pytest.raises(ValueError):
            accepted_invitation.accept(IdFactory())


# ═══════════════════════════════════════════════════════════════════════════
# Отклонение
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestInvitationDecline:
    def test_decline(self, email_invitation: Invitation) -> None:
        email_invitation.decline()
        assert email_invitation.status == InvitationStatus.DECLINED

    def test_decline_emits_event(self, email_invitation: Invitation) -> None:
        email_invitation.decline()
        events = email_invitation.clear_domain_events()
        assert any(isinstance(e, InvitationDeclined) for e in events)

    def test_decline_non_pending_raises(self, accepted_invitation: Invitation) -> None:
        with pytest.raises(ValueError):
            accepted_invitation.decline()


# ═══════════════════════════════════════════════════════════════════════════
# Отзыв
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestInvitationRevoke:
    def test_revoke(self, email_invitation: Invitation) -> None:
        email_invitation.revoke()
        assert email_invitation.status == InvitationStatus.REVOKED

    def test_revoke_emits_event(self, email_invitation: Invitation) -> None:
        email_invitation.revoke()
        events = email_invitation.clear_domain_events()
        assert any(isinstance(e, InvitationRevoked) for e in events)

    def test_revoke_non_pending_raises(self, accepted_invitation: Invitation) -> None:
        with pytest.raises(ValueError):
            accepted_invitation.revoke()


# ═══════════════════════════════════════════════════════════════════════════
# Использование ссылки
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestInvitationLinkUsage:
    def test_increment_link_usage(self, link_invitation: Invitation) -> None:
        link_invitation.increment_link_usage()
        assert link_invitation.link is not None
        assert link_invitation.link.used_count == 1

    def test_increment_link_usage_expired_raises(self, any_org_id: Id, any_role_id: Id, any_owner_id: Id) -> None:
        past = datetime.now(tz=timezone.utc) - timedelta(hours=1)
        token = InvitationToken(value="expired", expires_at=past)
        inv = Invitation(
            org_id=any_org_id, link=token, role_id=any_role_id, invited_by=any_owner_id,
        )
        with pytest.raises(InvitationLinkExpiredException):
            inv.increment_link_usage()

    def test_increment_link_usage_max_uses_exceeded_raises(
        self, any_org_id: Id, any_role_id: Id, any_owner_id: Id,
    ) -> None:
        token = InvitationToken(value="limited", max_uses=1, used_count=1)
        inv = Invitation(
            org_id=any_org_id, link=token, role_id=any_role_id, invited_by=any_owner_id,
        )
        with pytest.raises(InvitationLinkMaxUsesExceededException):
            inv.increment_link_usage()

    def test_increment_link_usage_on_email_invitation_is_noop(self, email_invitation: Invitation) -> None:
        email_invitation.increment_link_usage()
        assert email_invitation.link is None


# ═══════════════════════════════════════════════════════════════════════════
# Истечение
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestInvitationExpiry:
    def test_expire_if_needed_link_expired(self, any_org_id: Id, any_role_id: Id, any_owner_id: Id) -> None:
        past = datetime.now(tz=timezone.utc) - timedelta(hours=1)
        token = InvitationToken(value="expired", expires_at=past)
        inv = Invitation(
            org_id=any_org_id, link=token, role_id=any_role_id, invited_by=any_owner_id,
        )
        inv.expire_if_needed()
        assert inv.status == InvitationStatus.EXPIRED

    def test_expire_if_needed_not_pending_is_noop(self, any_org_id: Id, any_role_id: Id, any_owner_id: Id) -> None:
        past = datetime.now(tz=timezone.utc) - timedelta(hours=1)
        token = InvitationToken(value="expired", expires_at=past)
        inv = Invitation(
            org_id=any_org_id, link=token, role_id=any_role_id, invited_by=any_owner_id,
        )
        inv.status = InvitationStatus.ACCEPTED
        inv.expire_if_needed()
        assert inv.status == InvitationStatus.ACCEPTED

    def test_expire_if_needed_email_invitation_is_noop(self, email_invitation: Invitation) -> None:
        email_invitation.expire_if_needed()
        assert email_invitation.status == InvitationStatus.PENDING
