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
from app.context.project.application.ports.integration.outboard.project_provider import (
    ProjectProvider,
)
from app.context.task.application.ports.integration.outboard.task_provider import (
    TaskProvider,
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

    Для построения «осмысленного» уведомления (с текстом комментария,
    названием задачи и проекта) handler также читает:

    * `payload.content_excerpt` — короткая выжимка содержимого комментария,
      приходит из `CommentAdded` (см. `comment_events.py`);
    * `TaskProvider.get_task` — title и project_id задачи (для task-target);
    * `ProjectProvider.get_project` — name проекта (для построения подписи
      «в проекте «<имя>»» и для project-target).

    Автору комментария уведомление не отправляется.
    """

    def __init__(
        self,
        notification_repo: NotificationRepository,
        event_bus: DomainEventBus,
        task_participant_port: TaskParticipantPort,
        project_member_port: ProjectMemberPort,
        task_provider: TaskProvider,
        project_provider: ProjectProvider,
    ) -> None:
        super().__init__()
        self._repo = notification_repo
        self._event_bus = event_bus
        self._task_participant_port = task_participant_port
        self._project_member_port = project_member_port
        # Outboard-порты других BC. В Notification BC мы их трактуем как
        # «read-only-проекции» — никаких команд через них не идёт.
        self._task_provider = task_provider
        self._project_provider = project_provider

    async def handle(self, event: dict[str, Any]) -> None:
        if event.get("event_type") != "CommentAdded":
            return

        payload = event.get("payload", {})
        target_type = payload.get("target_type", "")
        target_id = payload.get("target_id", "")
        comment_id = payload.get("comment_id", "")
        author_id = payload.get("author_id")
        # Текстовая выжимка комментария: лучшее, что у нас есть для тела
        # уведомления. Если поле отсутствует (старые события) — fallback
        # на пустую строку, тело всё равно сформируется осмысленно.
        excerpt: str = (payload.get("content_excerpt") or "").strip()

        if not target_id or not comment_id:
            return

        # Сюда соберём `data` для notification — фронт уже знает, как из
        # этого построить deep-link и подписи. Поля:
        #   target_type/target_id — оригинал (для совместимости и роутинга);
        #   task_id / project_id  — конкретно то, на что нужно линковаться;
        #   task_title / project_name — для inline-подписей в UI;
        #   content_excerpt — текст комментария.
        data: dict[str, Any] = {
            "target_type": target_type,
            "target_id": target_id,
            "comment_id": comment_id,
            "content_excerpt": excerpt,
        }
        # Не публикуем author_id если он пустой (системный комментарий).
        if author_id:
            data["author_id"] = author_id

        task_title = ""
        project_name = ""

        if target_type == "task":
            recipient_ids = await self._task_participant_port.get_task_participants(
                target_id
            )
            notification_type = NotificationType.TASK_COMMENT

            # Подтягиваем мин. контекст задачи (title + project_id), чтобы
            # frontend смог сразу подписать карточку «<task> · <project>»
            # без N+1 запросов на ProjectBoardPage.
            try:
                task_dto = await self._task_provider.get_task(target_id)
            except Exception as exc:  # noqa: BLE001 — best-effort enrichment
                logger.warning("OnCommentAddedNotify: get_task failed", error=str(exc))
                task_dto = None
            if task_dto is not None:
                task_title = task_dto.title or ""
                data["task_id"] = task_dto.id
                if task_dto.project_id:
                    data["project_id"] = task_dto.project_id
                    try:
                        project_dto = await self._project_provider.get_project(
                            task_dto.project_id
                        )
                    except Exception as exc:  # noqa: BLE001
                        logger.warning(
                            "OnCommentAddedNotify: get_project failed",
                            error=str(exc),
                        )
                        project_dto = None
                    if project_dto is not None:
                        project_name = project_dto.name or ""
            else:
                # Бэкенд не смог распознать задачу — оставляем хотя бы
                # сам target_id как task_id, чтобы клик из уведомления
                # всё равно повёл нас на правильный URL.
                data["task_id"] = target_id
        elif target_type == "project":
            recipient_ids = await self._project_member_port.get_project_members(
                target_id
            )
            notification_type = NotificationType.PROJECT_COMMENT
            data["project_id"] = target_id
            try:
                project_dto = await self._project_provider.get_project(target_id)
            except Exception as exc:  # noqa: BLE001
                logger.warning("OnCommentAddedNotify: get_project failed", error=str(exc))
                project_dto = None
            if project_dto is not None:
                project_name = project_dto.name or ""
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

        if task_title:
            data["task_title"] = task_title
        if project_name:
            data["project_name"] = project_name

        # Тело уведомления = текст комментария (или fallback), плюс
        # короткая подпись контекста «<task> · <project>», если есть.
        # Это то, что пользователь увидит inline в карточке уведомления
        # без необходимости открывать таск-detail.
        excerpt_part = excerpt if excerpt else "Новый комментарий"
        ctx_parts: list[str] = []
        if task_title:
            ctx_parts.append(task_title)
        if project_name:
            ctx_parts.append(project_name)
        suffix = ""
        if ctx_parts:
            suffix = f" — {' · '.join(ctx_parts)}"
        body = f"{excerpt_part}{suffix}"

        recipients = [uid for uid in recipient_ids if uid != author_id]
        for user_id in recipients:
            notification = Notification.create(
                recipient_id=Id.from_string(user_id),
                notification_type=notification_type,
                title="Новый комментарий",
                body=body,
                priority=NotificationPriority.LOW,
                channels=[ChannelType.IN_APP],
                data=data,
            )
            await self._repo.add(notification)
            await self._event_bus.publish_all(notification.clear_domain_events())
