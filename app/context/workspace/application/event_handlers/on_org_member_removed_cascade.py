from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.repositories.workspace_membership_repository import WorkspaceMembershipRepository
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository


class OnOrgMemberRemovedCascade(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события OrgMemberRemoved из Organization BC.

    Удаляет пользователя из всех workspace, принадлежащих организации.
    Подписывается на топик «organization.events».
    """

    def __init__(
        self,
        membership_repo: WorkspaceMembershipRepository,
        workspace_repo: WorkspaceRepository,
    ) -> None:
        super().__init__()
        self._membership_repo = membership_repo
        self._workspace_repo = workspace_repo

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "OrgMemberRemoved":
            return

        payload = event.get("payload", {})
        org_id_str = payload.get("org_id")
        user_id_str = payload.get("user_id")
        
        if not org_id_str or not user_id_str:
            self._logger.warning(
                "OrgMemberRemoved missing org_id or user_id",
                raw_event=event,
            )
            return

        org_id = Id.from_string(org_id_str)
        user_id = Id.from_string(user_id_str)

        # Получаем все workspace организации
        workspaces = await self._workspace_repo.get_by_organization(org_id)
        
        removed_count = 0
        for workspace in workspaces:
            membership = await self._membership_repo.get_by_workspace_id(workspace.id)
            if membership is None:
                continue

            # Проверяем, является ли пользователь участником
            member = membership._find_member(user_id)
            if member is None:
                continue

            # Проверяем, не является ли пользователь владельцем
            is_owner = user_id in workspace.owner_ids
            if is_owner:
                self._logger.warning(
                    "Skipping removal of owner from workspace",
                    user_id=str(user_id),
                    workspace_id=str(workspace.id),
                    org_id=str(org_id),
                )
                continue

            membership.remove_member(user_id, is_owner=False)
            await self._membership_repo.update(membership)
            removed_count += 1

        self._logger.info(
            "Removed user from org workspaces",
            user_id=str(user_id),
            org_id=str(org_id),
            count=removed_count,
        )
