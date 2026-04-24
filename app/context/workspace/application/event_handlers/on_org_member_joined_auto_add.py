from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.repositories.workspace_membership_repository import WorkspaceMembershipRepository
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository
from app.context.workspace.domain.repositories.workspace_role_repository import WorkspaceRoleRepository


class OnOrgMemberJoinedAutoAdd(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события OrgMemberJoined из Organization BC.

    Подписывается на топик «organization.events».
    Если workspace привязан к организации и auto_add_from_org=True,
    автоматически добавляет нового участника организации в workspace.

    Идемпотентность: пропускает, если участник уже в workspace.
    """

    def __init__(
        self,
        ws_repo: WorkspaceRepository,
        membership_repo: WorkspaceMembershipRepository,
        role_repo: WorkspaceRoleRepository,
    ) -> None:
        super().__init__()
        self._ws_repo = ws_repo
        self._membership_repo = membership_repo
        self._role_repo = role_repo

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "OrgMemberJoined":
            return

        payload = event.get("payload", {})
        org_id_str = payload.get("org_id")
        user_id_str = payload.get("user_id")
        if not org_id_str or not user_id_str:
            self._logger.warning(
                "OrgMemberJoined event missing org_id or user_id",
                event_data=event,
            )
            return

        org_id = Id.from_string(org_id_str)
        user_id = Id.from_string(user_id_str)

        workspaces = await self._ws_repo.get_by_organization(org_id)

        for ws in workspaces:
            if not ws.membership_policy.auto_add_from_org:
                continue

            membership = await self._membership_repo.get_by_workspace_id(ws.id)
            if membership is None:
                continue

            existing = membership._find_member(user_id)
            if existing is not None:
                continue

            default_role_name = ws.membership_policy.default_role
            role = await self._role_repo.get_by_name(default_role_name)
            role_id = role.id if role else Id.generate()

            membership.add_member_from_org(user_id=user_id, role_id=role_id)
            await self._membership_repo.update(membership)

            self._logger.info(
                "Auto-added org member to workspace",
                user_id=user_id_str,
                workspace_id=str(ws.id),
            )
