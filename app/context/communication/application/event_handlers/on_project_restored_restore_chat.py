"""Обработчик ``ProjectRestored`` / ``ProjectReactivated`` → разархивация чата.

Подписан на оба события: оба возвращают проект в активное состояние и
должны возвращать его чат в обиход.
"""
from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.domain.repositories.chat_repository import (
    ChatRepository,
)


_HANDLED_EVENTS = {"ProjectRestored", "ProjectReactivated"}


class OnProjectRestoredRestoreChat(BaseEventHandler[dict[str, Any]]):
    """Разархивирует проектный чат при восстановлении/реактивации проекта."""

    def __init__(
        self,
        chat_repo: ChatRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._chat_repo = chat_repo
        self._event_bus = event_bus

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type not in _HANDLED_EVENTS:
            return

        payload = event.get("payload", {})
        project_id_str = payload.get("project_id")
        if not project_id_str:
            self._logger.warning(
                "Project restore event missing project_id",
                event_type=event_type,
                raw_event=event,
            )
            return

        project_id = Id.from_string(project_id_str)
        chat = await self._chat_repo.get_by_project_id(project_id)
        if chat is None or not chat.is_archived:
            return

        chat.restore()
        await self._chat_repo.update(chat)
        await self._event_bus.publish_all(chat.clear_domain_events())
        self._logger.info(
            "Project chat restored",
            chat_id=str(chat.id),
            project_id=project_id_str,
            trigger=event_type,
        )
