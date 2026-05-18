"""Обработчик ``ProjectArchived`` → архивация проектного чата.

Чат не удаляется, история переписки сохраняется — но новые сообщения
становятся недоступны, и чат скрывается из списка по умолчанию
(``GET /chats?include_archived=false``).
"""
from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.domain.repositories.chat_repository import (
    ChatRepository,
)


class OnProjectArchivedArchiveChat(BaseEventHandler[dict[str, Any]]):
    """Архивирует проектный чат при архивации проекта."""

    def __init__(
        self,
        chat_repo: ChatRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._chat_repo = chat_repo
        self._event_bus = event_bus

    async def handle(self, event: dict[str, Any]) -> None:
        if event.get("event_type") != "ProjectArchived":
            return

        payload = event.get("payload", {})
        project_id_str = payload.get("project_id")
        if not project_id_str:
            self._logger.warning(
                "ProjectArchived missing project_id",
                raw_event=event,
            )
            return

        project_id = Id.from_string(project_id_str)
        chat = await self._chat_repo.get_by_project_id(project_id)
        if chat is None or chat.is_archived:
            return

        chat.archive()
        await self._chat_repo.update(chat)
        await self._event_bus.publish_all(chat.clear_domain_events())
        self._logger.info(
            "Project chat archived",
            chat_id=str(chat.id),
            project_id=project_id_str,
        )
