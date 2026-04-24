from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository


class OnSecurityPolicyCascade(BaseEventHandler[dict[str, Any]]):
    """
    Intra-BC обработчик события SecurityPolicyChanged.

    Подписывается на топик «workspace.events».
    При изменении SecurityPolicy родительского workspace
    каскадно обновляет дочерние workspace, у которых
    inherit_from_parent=True.
    """

    def __init__(self, ws_repo: WorkspaceRepository) -> None:
        super().__init__()
        self._ws_repo = ws_repo

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "SecurityPolicyChanged":
            return

        payload = event.get("payload", {})
        workspace_id_str = payload.get("workspace_id")
        if not workspace_id_str:
            return

        parent_id = Id.from_string(workspace_id_str)
        parent = await self._ws_repo.get_by_id(parent_id)
        if parent is None:
            return

        children = await self._ws_repo.get_children(parent_id)
        for child in children:
            if not child.security_policy.inherit_from_parent:
                continue

            child.update_security_policy(parent.security_policy)
            await self._ws_repo.update(child)

            self._logger.info(
                "Cascaded security policy to child workspace",
                parent_id=workspace_id_str,
                child_id=str(child.id),
            )
