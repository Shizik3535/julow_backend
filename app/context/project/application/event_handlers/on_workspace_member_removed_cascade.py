from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.repositories.project_membership_repository import ProjectMembershipRepository
from app.context.project.domain.repositories.project_repository import ProjectRepository


class OnWorkspaceMemberRemovedCascade(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события WorkspaceMemberRemoved из Workspace BC.

    Удаляет пользователя из всех проектов workspace.
    Подписывается на топик «workspace.events».
    """

    def __init__(
        self,
        project_repo: ProjectRepository,
        membership_repo: ProjectMembershipRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._project_repo = project_repo
        self._membership_repo = membership_repo
        self._event_bus = event_bus

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "WorkspaceMemberRemoved":
            return

        payload = event.get("payload", {})
        workspace_id_str = payload.get("workspace_id")
        user_id_str = payload.get("user_id")
        
        if not workspace_id_str or not user_id_str:
            self._logger.warning(
                "WorkspaceMemberRemoved missing workspace_id or user_id",
                raw_event=event,
            )
            return

        workspace_id = Id.from_string(workspace_id_str)
        user_id = Id.from_string(user_id_str)

        projects = await self._project_repo.get_by_workspace(workspace_id)
        
        removed_count = 0
        for project in projects:
            membership = await self._membership_repo.get_by_project_id(project.id)
            if membership is None:
                continue

            member = membership._find_member(user_id)
            if member is None:
                continue

            # Проверяем, не является ли пользователь владельцем
            is_owner = user_id in project.owner_ids
            if is_owner:
                self._logger.warning(
                    "Skipping removal of owner from project",
                    user_id=str(user_id),
                    project_id=str(project.id),
                    workspace_id=str(workspace_id),
                )
                continue

            membership.remove_member(user_id, is_owner=False)
            await self._membership_repo.update(membership)
            await self._event_bus.publish_all(membership.clear_domain_events())
            removed_count += 1

        self._logger.info(
            "Removed user from workspace projects",
            user_id=str(user_id),
            workspace_id=str(workspace_id),
            count=removed_count,
        )
