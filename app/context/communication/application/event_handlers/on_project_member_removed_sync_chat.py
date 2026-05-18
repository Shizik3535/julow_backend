"""Обработчик ``ProjectMemberRemoved`` → удаление участника из проектного чата.

Идемпотентен: если чата нет или участника в нём нет — ничего не делает.
Не падает, даже если чат архивирован: в этом случае запись о членстве
просто удаляется, чтобы состав не противоречил состоянию проекта.
"""
from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.domain.repositories.chat_repository import (
    ChatRepository,
)


class OnProjectMemberRemovedSyncChat(BaseEventHandler[dict[str, Any]]):
    """Удаляет участника из проектного чата при удалении из проекта."""

    def __init__(
        self,
        chat_repo: ChatRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._chat_repo = chat_repo
        self._event_bus = event_bus

    async def handle(self, event: dict[str, Any]) -> None:
        if event.get("event_type") != "ProjectMemberRemoved":
            return

        payload = event.get("payload", {})
        project_id_str = payload.get("project_id")
        user_id_str = payload.get("user_id")
        if not project_id_str or not user_id_str:
            self._logger.warning(
                "ProjectMemberRemoved missing project_id or user_id",
                raw_event=event,
            )
            return

        project_id = Id.from_string(project_id_str)
        user_id = Id.from_string(user_id_str)

        chat = await self._chat_repo.get_by_project_id(project_id)
        if chat is None:
            return

        chat.system_remove_member(user_id)
        await self._chat_repo.update(chat)
        await self._event_bus.publish_all(chat.clear_domain_events())
        self._logger.info(
            "Project chat member removed",
            chat_id=str(chat.id),
            project_id=project_id_str,
            user_id=user_id_str,
        )
