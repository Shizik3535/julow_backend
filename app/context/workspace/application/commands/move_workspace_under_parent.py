from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import (
    CircularWorkspaceHierarchyException,
    ParentWorkspaceNotFoundException,
    WorkspaceNotFoundException,
)
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository


MAX_HIERARCHY_DEPTH = 3


class MoveWorkspaceUnderParentCommand(BaseCommand):
    """
    Команда перемещения workspace в иерархию.

    Если parent_workspace_id=None — отсоединить от родителя (detach).

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        workspace_id: ID workspace.
        parent_workspace_id: ID родительского workspace (None → detach).
    """

    caller_id: str
    workspace_id: str
    parent_workspace_id: str | None = None


class MoveWorkspaceUnderParentHandler(BaseCommandHandler[MoveWorkspaceUnderParentCommand, None]):
    """
    Обработчик перемещения workspace в иерархию.

    Проверяет:
    - Существование родительского workspace.
    - Отсутствие циклических ссылок (обход parent chain).
    - Глубину иерархии (макс. MAX_HIERARCHY_DEPTH).
    """

    REQUIRED_PERMISSION = "ws.settings.write"

    def __init__(
        self,
        ws_repo: WorkspaceRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._ws_repo = ws_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: MoveWorkspaceUnderParentCommand) -> None:
        ws_id = Id.from_string(command.workspace_id)

        ws = await self._ws_repo.get_by_id(ws_id)
        if ws is None:
            raise WorkspaceNotFoundException(command.workspace_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            workspace_id=ws_id,
            permission=self.REQUIRED_PERMISSION,
        )

        if command.parent_workspace_id is None:
            ws.detach_from_parent()
            await self._ws_repo.update(ws)
            await self._event_bus.publish_all(ws.clear_domain_events())
            return

        parent_id = Id.from_string(command.parent_workspace_id)
        parent = await self._ws_repo.get_by_id(parent_id)
        if parent is None:
            raise ParentWorkspaceNotFoundException(command.parent_workspace_id)

        visited: set[str] = {command.workspace_id}
        current = parent
        depth = 1
        while current.parent_workspace_id is not None:
            current_id_str = str(current.parent_workspace_id)
            if current_id_str in visited:
                raise CircularWorkspaceHierarchyException()
            visited.add(current_id_str)
            depth += 1
            if depth > MAX_HIERARCHY_DEPTH:
                raise CircularWorkspaceHierarchyException()
            ancestor = await self._ws_repo.get_by_id(current.parent_workspace_id)
            if ancestor is None:
                break
            current = ancestor

        if depth >= MAX_HIERARCHY_DEPTH:
            raise CircularWorkspaceHierarchyException()

        ws.move_under_parent(parent_workspace_id=parent_id)
        await self._ws_repo.update(ws)
        await self._event_bus.publish_all(ws.clear_domain_events())
