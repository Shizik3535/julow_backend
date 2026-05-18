from __future__ import annotations

from typing import Any

from app.context.project.application.dto.board_dto import BoardDTO
from app.context.project.application.ports.integration.outboard.board_provider import (
    BoardProvider,
)
from app.context.project.domain.repositories.board_repository import BoardRepository
from app.shared.domain.value_objects.id_vo import Id


class BoardProviderAdapter(BoardProvider):
    """
    Реализация outboard-порта BoardProvider.

    Делегирует в BoardRepository для предоставления данных доски другим BC.
    """

    def __init__(self, repo: BoardRepository) -> None:
        self._repo = repo

    async def get_board(self, project_id: str) -> BoardDTO | None:
        board = await self._repo.get_by_project_id(Id.from_string(project_id))
        if board is None:
            return None
        return self._to_dto(board)

    async def get_workflow_statuses(self, project_id: str) -> list[dict[str, Any]]:
        board = await self._repo.get_by_project_id(Id.from_string(project_id))
        if board is None:
            return []
        return [
            {
                "id": str(s.id),
                "name": s.name,
                "color": str(s.color) if s.color else None,
                "icon": s.icon,
                "order": s.order,
                "is_default": s.is_default,
                "category": s.category.value,
            }
            for s in board.workflow_statuses
        ]

    async def get_default_status_id(self, project_id: str) -> str | None:
        board = await self._repo.get_by_project_id(Id.from_string(project_id))
        if board is None:
            return None
        for s in board.workflow_statuses:
            if s.is_default:
                return str(s.id)
        return None

    async def is_transition_allowed(
        self, project_id: str, from_status_id: str, to_status_id: str
    ) -> bool:
        board = await self._repo.get_by_project_id(Id.from_string(project_id))
        if board is None:
            return False
        # Permissive fallback: если у board'а нет явно настроенных transitions —
        # разрешаем любые переходы. Как только админ добавит хотя бы один
        # transition, workflow становится строгим (whitelist).
        if not board.workflow_transitions:
            return True
        for t in board.workflow_transitions:
            if str(t.from_status_id) == from_status_id and str(t.to_status_id) == to_status_id:
                return True
        return False

    async def get_columns(self, project_id: str) -> list[dict[str, Any]]:
        board = await self._repo.get_by_project_id(Id.from_string(project_id))
        if board is None:
            return []
        return [
            {
                "id": str(c.id),
                "name": c.name,
                "order": c.order,
                "color": str(c.color) if c.color else None,
                "wip_limit": c.wip_limit.value if c.wip_limit else None,
            }
            for c in board.columns
        ]

    @staticmethod
    def _to_dto(board) -> BoardDTO:
        return BoardDTO(
            id=str(board.id),
            project_id=str(board.project_id),
            columns=[
                {
                    "id": str(c.id),
                    "name": c.name,
                    "order": c.order,
                    "color": str(c.color) if c.color else None,
                    "wip_limit": c.wip_limit.value if c.wip_limit else None,
                }
                for c in board.columns
            ],
            swimlanes=[
                {
                    "id": str(s.id),
                    "name": s.name,
                    "order": s.order,
                    "group_by": s.group_by.value,
                    "group_value": s.group_value,
                }
                for s in board.swimlanes
            ],
            workflow_statuses=[
                {
                    "id": str(s.id),
                    "name": s.name,
                    "color": str(s.color) if s.color else None,
                    "icon": s.icon,
                    "order": s.order,
                    "is_default": s.is_default,
                    "category": s.category.value,
                }
                for s in board.workflow_statuses
            ],
            workflow_transitions=[
                {
                    "id": str(t.id),
                    "from_status_id": str(t.from_status_id),
                    "to_status_id": str(t.to_status_id),
                    "name": t.name,
                    "trigger": t.trigger.value if t.trigger else None,
                    "required_permission": t.required_permission,
                }
                for t in board.workflow_transitions
            ],
            views=[
                {
                    "id": str(v.id),
                    "name": v.name,
                    "is_default": v.is_default,
                    "is_shared": v.is_shared,
                    "owner_id": str(v.owner_id) if v.owner_id else None,
                }
                for v in board.views
            ],
            automation_rules=[
                {
                    "id": str(r.id),
                    "name": r.name,
                    "trigger": r.trigger.value,
                    "action": r.action.value,
                    "is_enabled": r.is_enabled,
                }
                for r in board.automation_rules
            ],
            created_at=board.created_at,
            updated_at=board.updated_at,
        )
