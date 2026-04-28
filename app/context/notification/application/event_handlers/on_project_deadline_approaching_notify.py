from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.application.ports.integration.inboard.project_member_port import (
    ProjectMemberPort,
)
from app.context.notification.domain.aggregates.notification import Notification
from app.context.notification.domain.repositories.notification_repository import NotificationRepository
from app.context.notification.domain.value_objects.notification_type import NotificationType
from app.context.notification.domain.value_objects.notification_priority import NotificationPriority
from app.context.notification.domain.value_objects.channel_type import ChannelType
from app.shared.application.messaging.domain_event_bus import DomainEventBus


class OnProjectDeadlineApproachingNotify(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события ProjectDeadlineApproaching из Project BC.

    Создаёт project_deadline_approaching уведомление для каждого участника проекта.
    """

    def __init__(
        self,
        notification_repo: NotificationRepository,
        event_bus: DomainEventBus,
        project_member_port: ProjectMemberPort,
    ) -> None:
        super().__init__()
        self._repo = notification_repo
        self._event_bus = event_bus
        self._project_member_port = project_member_port

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "ProjectDeadlineApproaching":
            return

        payload = event.get("payload", {})
        project_id = payload.get("project_id", "")
        deadline = payload.get("deadline", "")
        if not project_id:
            return

        member_ids = await self._project_member_port.get_project_members(project_id)
        if not member_ids:
            return

        for user_id in member_ids:
            # Дедупликация: не создавать повторное уведомление
            if await self._repo.has_unread_by_type_and_target(
                recipient_id=Id.from_string(user_id),
                notification_type=NotificationType.PROJECT_DEADLINE_APPROACHING,
                target_key=project_id,
            ):
                continue

            notification = Notification.create(
                recipient_id=Id.from_string(user_id),
                notification_type=NotificationType.PROJECT_DEADLINE_APPROACHING,
                title="Приближение дедлайна проекта",
                body="Дедлайн проекта приближается.",
                priority=NotificationPriority.NORMAL,
                channels=[ChannelType.IN_APP, ChannelType.EMAIL],
                data={"project_id": project_id, "deadline": deadline},
            )
            await self._repo.add(notification)
            await self._event_bus.publish_all(notification.clear_domain_events())
