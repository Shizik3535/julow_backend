"""Обработчик события ``CommentAdded`` (Communication BC)."""

from __future__ import annotations

from typing import Any

from app.core.logging import get_logger
from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.application.ports.integration.inboard.project_member_port import (
    ProjectMemberPort,
)
from app.context.notification.application.ports.integration.inboard.task_participant_port import (
    TaskParticipantPort,
)
from app.context.notification.domain.aggregates.notification import Notification
from app.context.notification.domain.repositories.notification_repository import (
    NotificationRepository,
)
from app.context.notification.domain.value_objects.channel_type import ChannelType
from app.context.notification.domain.value_objects.notification_priority import (
    NotificationPriority,
)
from app.context.notification.domain.value_objects.notification_type import (
    NotificationType,
)

logger = get_logger(__name__)


class OnCommentAddedNotify(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события ``CommentAdded`` из Communication BC.

    Маршрутизация по ``target_type``:

    * ``task``    — уведомляются все участники задачи через :class:`TaskParticipantPort`;
    * ``project`` — уведомляются все участники проекта через :class:`ProjectMemberPort`;
    * остальные (``epic``, ``sprint``, ``milestone`` и т.д.) пока не
      поддерживаются: логируется предупреждение и событие игнорируется
      до появления соответствующих inboard-портов.

    Автору комментария уведомление не отправляется.
    """

    def __init__(
        self,
        notification_repo: NotificationRepository,
        event_bus: DomainEventBus,
        task_participant_port: TaskParticipantPort,
        project_member_port: ProjectMemberPort,
    ) -> None:
        super().__init__()
        self._repo = notification_repo
        self._event_bus = event_bus
        self._task_participant_port = task_participant_port
        self._project_member_port = project_member_port

    async def handle(self, event: dict[str, Any]) -> None:
        if event.get("event_type") != "CommentAdded":
            return

        payload = event.get("payload", {})
        target_type = payload.get("target_type", "")
        target_id = payload.get("target_id", "")
        comment_id = payload.get("comment_id", "")
        author_id = payload.get("author_id")

        if not target_id or not comment_id:
            return

        # Маршрутизация по target_type: получаем список получателей + тип уведомления.
        if target_type == "task":
            recipient_ids = await self._task_participant_port.get_task_participants(
                target_id
            )
            notification_type = NotificationType.TASK_COMMENT
            body = "К задаче добавлен новый комментарий."
        elif target_type == "project":
            recipient_ids = await self._project_member_port.get_project_members(
                target_id
            )
            notification_type = NotificationType.PROJECT_COMMENT
            body = "К проекту добавлен новый комментарий."
        else:
            # epic/sprint/milestone пока не поддерживаются — нужны отдельные inboard-порты.
            logger.warning(
                "OnCommentAddedNotify: target_type не поддерживается, уведомление пропущено",
                target_type=target_type,
                comment_id=comment_id,
                target_id=target_id,
            )
            return

        if not recipient_ids:
            return

        recipients = [uid for uid in recipient_ids if uid != author_id]
        for user_id in recipients:
            notification = Notification.create(
                recipient_id=Id.from_string(user_id),
                notification_type=notification_type,
                title="Новый комментарий",
                body=body,
                priority=NotificationPriority.LOW,
                channels=[ChannelType.IN_APP],
                data={
                    "target_type": target_type,
                    "target_id": target_id,
                    "comment_id": comment_id,
                },
            )
            await self._repo.add(notification)
            await self._event_bus.publish_all(notification.clear_domain_events())
