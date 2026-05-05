"""Интеграционные тесты OnProjectOverdueNotify — обработчик уведомлений о просроченном проекте."""

from unittest.mock import AsyncMock, patch

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.application.event_handlers.on_project_overdue_notify import OnProjectOverdueNotify
from app.context.notification.domain.value_objects.notification_type import NotificationType


@pytest.mark.integration
class TestOnProjectOverdueNotify:
    """Тесты обработчика события ProjectOverdue."""

    @pytest.fixture
    def notification_repo(self) -> AsyncMock:
        repo = AsyncMock()
        repo.has_unread_by_type_and_target.return_value = False
        repo.add = AsyncMock()
        return repo

    @pytest.fixture
    def event_bus(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def project_member_port(self) -> AsyncMock:
        port = AsyncMock()
        port.get_project_members.return_value = []
        return port

    @pytest.fixture
    def handler(self, notification_repo, event_bus, project_member_port) -> OnProjectOverdueNotify:
        return OnProjectOverdueNotify(
            notification_repo=notification_repo,
            event_bus=event_bus,
            project_member_port=project_member_port,
        )

    async def test_ignores_other_event_types(self, handler, notification_repo) -> None:
        event = {"event_type": "ProjectDeadlineApproaching", "payload": {"project_id": str(Id.generate()), "deadline": "2025-01-01"}}
        await handler.handle(event)
        notification_repo.add.assert_not_called()

    async def test_ignores_event_without_project_id(self, handler, notification_repo) -> None:
        event = {"event_type": "ProjectOverdue", "payload": {"deadline": "2025-01-01"}}
        await handler.handle(event)
        notification_repo.add.assert_not_called()

    async def test_creates_notification_for_each_member(
        self, handler, notification_repo, project_member_port
    ) -> None:
        member1 = str(Id.generate())
        member2 = str(Id.generate())
        project_id = str(Id.generate())
        project_member_port.get_project_members.return_value = [member1, member2]

        event = {
            "event_type": "ProjectOverdue",
            "payload": {"project_id": project_id, "deadline": "2025-01-01"},
        }
        await handler.handle(event)

        assert notification_repo.add.call_count == 2

    async def test_skips_already_notified_members(
        self, handler, notification_repo, project_member_port
    ) -> None:
        member1 = str(Id.generate())
        member2 = str(Id.generate())
        project_id = str(Id.generate())
        project_member_port.get_project_members.return_value = [member1, member2]

        # member1 already has unread notification
        async def _has_unread(recipient_id, notification_type, target_key):
            return str(recipient_id) == member1
        notification_repo.has_unread_by_type_and_target.side_effect = _has_unread

        event = {
            "event_type": "ProjectOverdue",
            "payload": {"project_id": project_id, "deadline": "2025-01-01"},
        }
        await handler.handle(event)

        # Only member2 gets a new notification
        assert notification_repo.add.call_count == 1

    async def test_no_members_no_notifications(
        self, handler, notification_repo, project_member_port
    ) -> None:
        project_member_port.get_project_members.return_value = []

        event = {
            "event_type": "ProjectOverdue",
            "payload": {"project_id": str(Id.generate()), "deadline": "2025-01-01"},
        }
        await handler.handle(event)

        notification_repo.add.assert_not_called()
