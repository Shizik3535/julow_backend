from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.repositories.workspace_membership_repository import WorkspaceMembershipRepository
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository


class OnOrgMemberDeactivatedCascade(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события OrgMemberDeactivated из Organization BC.

    Деактивирует пользователя во всех workspace, принадлежащих организации.
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
        if event_type != "OrgMemberDeactivated":
            return

        payload = event.get("payload", {})
        org_id_str = payload.get("org_id")
        user_id_str = payload.get("user_id")
        
        if not org_id_str or not user_id_str:
            self._logger.warning(
                "OrgMemberDeactivated missing org_id or user_id",
                raw_event=event,
            )
            return

        org_id = Id.from_string(org_id_str)
        user_id = Id.from_string(user_id_str)

        # Получаем все workspace организации
        workspaces = await self._workspace_repo.get_by_organization(org_id)
        
        deactivated_count = 0
        for workspace in workspaces:
            membership = await self._membership_repo.get_by_workspace_id(workspace.id)
            if membership is None:
                continue

            # Проверяем, является ли пользователь участником
            member = membership._find_member(user_id)
            if member is None:
                continue

            # Проверяем текущий статус
            if not member.is_active:
                continue  # Уже деактивирован

            member.deactivate()
            await self._membership_repo.update(membership)
            deactivated_count += 1

        self._logger.info(
            "Deactivated user in org workspaces",
            user_id=str(user_id),
            org_id=str(org_id),
            count=deactivated_count,
        )
