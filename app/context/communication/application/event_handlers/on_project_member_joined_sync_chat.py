"""Обработчик ``ProjectMemberJoined`` → синхронизация проектного чата.

Гарантирует наличие проектного чата для любого проекта (даже с одним
владельцем) и добавляет нового участника в существующий чат. Если чат
уже существует — просто добавляет участника (повторно — идемпотентно).
"""
from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.domain.aggregates.chat import Chat
from app.context.communication.domain.repositories.chat_repository import (
    ChatRepository,
)
from app.context.project.application.ports.integration.outboard.project_membership_provider import (
    ProjectMembershipProvider,
)
from app.context.project.application.ports.integration.outboard.project_provider import (
    ProjectProvider,
)


_MIN_PROJECT_CHAT_MEMBERS = 1


class OnProjectMemberJoinedSyncChat(BaseEventHandler[dict[str, Any]]):
    """Поддерживает состав проектного чата при добавлении участника проекта."""

    def __init__(
        self,
        chat_repo: ChatRepository,
        project_provider: ProjectProvider,
        project_membership_provider: ProjectMembershipProvider,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._chat_repo = chat_repo
        self._project_provider = project_provider
        self._project_membership_provider = project_membership_provider
        self._event_bus = event_bus

    async def handle(self, event: dict[str, Any]) -> None:
        if event.get("event_type") != "ProjectMemberJoined":
            return

        payload = event.get("payload", {})
        project_id_str = payload.get("project_id")
        user_id_str = payload.get("user_id")
        if not project_id_str or not user_id_str:
            self._logger.warning(
                "ProjectMemberJoined missing project_id or user_id",
                raw_event=event,
            )
            return

        project_id = Id.from_string(project_id_str)
        user_id = Id.from_string(user_id_str)

        member_ids = await self._project_membership_provider.get_project_member_ids(
            project_id_str,
        )
        if len(member_ids) < _MIN_PROJECT_CHAT_MEMBERS:
            # Проект без активных участников — нечего синхронизировать.
            return

        chat = await self._chat_repo.get_by_project_id(project_id)
        if chat is None:
            chat = await self._create_project_chat(
                project_id=project_id,
                member_ids=member_ids,
            )
            if chat is None:
                return
        else:
            if chat.is_archived:
                # Проект может быть восстановлен раньше, но если чат всё ещё в
                # архиве — не мутируем его. Восстановление управляется
                # отдельным обработчиком ``ProjectRestored/Reactivated``.
                return
            chat.system_add_member(user_id)
            await self._chat_repo.update(chat)
            await self._event_bus.publish_all(chat.clear_domain_events())

    async def _create_project_chat(
        self,
        project_id: Id,
        member_ids: list[str],
    ) -> Chat | None:
        project_dto = await self._project_provider.get_project(str(project_id))
        if project_dto is None:
            self._logger.warning(
                "Cannot create project chat — project not found",
                project_id=str(project_id),
            )
            return None

        owner_ids = list(getattr(project_dto, "owner_ids", []) or [])
        owner_id: Id | None = (
            Id.from_string(owner_ids[0]) if owner_ids else None
        )
        workspace_id_str = getattr(project_dto, "workspace_id", None)
        workspace_id = (
            Id.from_string(workspace_id_str) if workspace_id_str else None
        )

        chat = Chat.create_project_chat(
            name=str(getattr(project_dto, "name", "") or f"Project {project_id}"),
            project_id=project_id,
            workspace_id=workspace_id,
            member_ids=[Id.from_string(uid) for uid in member_ids],
            owner_id=owner_id,
        )
        await self._chat_repo.add(chat)
        await self._event_bus.publish_all(chat.clear_domain_events())
        self._logger.info(
            "Project chat created",
            chat_id=str(chat.id),
            project_id=str(project_id),
            members=len(member_ids),
        )
        return chat
