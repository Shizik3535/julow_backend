"""Обработчик ``ProjectDeletionRequested`` → архивация проектного чата.

Соответствует требованию «при удалении проекта чат сохраняется, но
переводится в архив». Удаление проекта в системе — soft-delete
(``PENDING_DELETION``), поэтому история чата остаётся доступна
владельцам/админам для аудита.
"""
from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.domain.repositories.chat_repository import (
    ChatRepository,
)


class OnProjectDeletionRequestedArchiveChat(BaseEventHandler[dict[str, Any]]):
    """Архивирует проектный чат при запросе удаления проекта."""

    def __init__(
        self,
        chat_repo: ChatRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._chat_repo = chat_repo
        self._event_bus = event_bus

    async def handle(self, event: dict[str, Any]) -> None:
        if event.get("event_type") != "ProjectDeletionRequested":
            return

        payload = event.get("payload", {})
        project_id_str = payload.get("project_id")
        if not project_id_str:
            self._logger.warning(
                "ProjectDeletionRequested missing project_id",
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
            "Project chat archived (deletion requested)",
            chat_id=str(chat.id),
            project_id=project_id_str,
        )
