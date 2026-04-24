"""Интеграционные тесты OnAccountDeletionRequestedCleanupMemberships (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.event_handlers.on_account_deletion_requested_cleanup_memberships import (
    OnAccountDeletionRequestedCleanupMemberships,
)


@pytest.mark.integration
class TestOnAccountDeletionRequestedCleanupMemberships:
    @pytest.fixture
    def handler(self, membership_repo):
        return OnAccountDeletionRequestedCleanupMemberships(
            membership_repo=membership_repo,
        )

    async def test_removes_user_from_all_orgs(
        self, handler, make_org_with_membership, membership_repo
    ) -> None:
        data = await make_org_with_membership()
        event = {
            "event_type": "AccountDeletionRequested",
            "payload": {"user_id": str(data["owner_id"])},
        }
        await handler.handle(event)
        membership = await membership_repo.get_by_org_id(data["org"].id)
        assert membership is not None
        assert not any(m.user_id == data["owner_id"] for m in membership.members)

    async def test_idempotent(self, handler, make_org_with_membership, membership_repo) -> None:
        data = await make_org_with_membership()
        event = {
            "event_type": "AccountDeletionRequested",
            "payload": {"user_id": str(data["owner_id"])},
        }
        await handler.handle(event)
        await handler.handle(event)  # second call should not raise

    async def test_missing_user_id_logs_warning(self, handler) -> None:
        event = {"event_type": "AccountDeletionRequested", "payload": {}}
        await handler.handle(event)  # should not raise

    async def test_wrong_event_type_ignored(self, handler) -> None:
        event = {"event_type": "SomeOtherEvent", "payload": {"user_id": str(Id.generate())}}
        await handler.handle(event)  # should not raise
