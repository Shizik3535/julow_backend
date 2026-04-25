from __future__ import annotations

from typing import Any

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.board_dto import BoardDTO
from app.context.project.application.exceptions.board_app_exceptions import BoardNotFoundException
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)
from app.context.project.domain.aggregates.board import Board
from app.context.project.domain.repositories.board_repository import BoardRepository


class GetBoardQuery(BaseQuery):
    """Запрос получения доски проекта."""

    caller_id: str
    project_id: str


class GetBoardHandler(BaseQueryHandler[GetBoardQuery, BoardDTO]):
    """Обработчик получения доски проекта."""

    REQUIRED_PERMISSION = "project.read"

    def __init__(self, board_repo: BoardRepository, permission_checker: ProjectPermissionCheckerPort) -> None:
        super().__init__()
        self._board_repo = board_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetBoardQuery) -> BoardDTO:
        board = await self._board_repo.get_by_project_id(Id.from_string(query.project_id))
        if board is None:
            raise BoardNotFoundException(query.project_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(query.caller_id),
            project_id=board.project_id,
            permission=self.REQUIRED_PERMISSION,
        )
        return self._to_dto(board)

    @staticmethod
    def _to_dto(b: Board) -> BoardDTO:
        columns: list[dict[str, Any]] = [
            {
                "id": str(c.id),
                "name": c.name,
                "order": c.order,
                "color": str(c.color) if c.color else None,
                "wip_limit": c.wip_limit.value if c.wip_limit else None,
                "status_mapping": str(c.status_mapping) if c.status_mapping else None,
            }
            for c in b.columns
        ]

        swimlanes: list[dict[str, Any]] = [
            {
                "id": str(s.id),
                "name": s.name,
                "order": s.order,
                "group_by": s.group_by.value,
                "group_value": s.group_value,
            }
            for s in b.swimlanes
        ]

        statuses: list[dict[str, Any]] = [
            {
                "id": str(ws.id),
                "name": ws.name,
                "color": str(ws.color) if ws.color else None,
                "icon": ws.icon,
                "order": ws.order,
                "is_default": ws.is_default,
                "category": ws.category.value,
            }
            for ws in b.workflow_statuses
        ]

        transitions: list[dict[str, Any]] = [
            {
                "id": str(t.id),
                "from_status_id": str(t.from_status_id),
                "to_status_id": str(t.to_status_id),
                "name": t.name,
                "required_permission": t.required_permission,
            }
            for t in b.workflow_transitions
        ]

        views: list[dict[str, Any]] = [
            {
                "id": str(v.id),
                "name": v.name,
                "config": {"view_type": v.config.view_type.value} if v.config else None,
                "is_default": v.is_default,
                "is_shared": v.is_shared,
                "owner_id": str(v.owner_id) if v.owner_id else None,
            }
            for v in b.views
        ]

        rules: list[dict[str, Any]] = [
            {
                "id": str(r.id),
                "name": r.name,
                "trigger": r.trigger.value,
                "action": r.action.value,
                "action_params": r.action_params,
                "is_enabled": r.is_enabled,
            }
            for r in b.automation_rules
        ]

        return BoardDTO(
            id=str(b.id),
            project_id=str(b.project_id),
            columns=columns,
            swimlanes=swimlanes,
            workflow_statuses=statuses,
            workflow_transitions=transitions,
            views=views,
            automation_rules=rules,
            created_at=b.created_at,
            updated_at=b.updated_at,
        )
