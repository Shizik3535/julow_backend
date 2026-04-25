from __future__ import annotations

from typing import Any

from app.context.project.application.ports.integration.outboard.board_provider import (
    BoardProvider,
)
from app.context.task.application.ports.integration.inboard.board_port import (
    BoardPort,
)


class BoardAdapter(BoardPort):
    """
    Реализация inboard-порта BoardPort для Task BC.

    Делегирует получение данных доски в outboard-порт
    Project BC (BoardProvider).
    """

    def __init__(self, board_provider: BoardProvider) -> None:
        self._provider = board_provider

    async def get_workflow_statuses(self, project_id: str) -> list[dict[str, Any]]:
        return await self._provider.get_workflow_statuses(project_id)

    async def get_default_status_id(self, project_id: str) -> str | None:
        return await self._provider.get_default_status_id(project_id)

    async def is_transition_allowed(
        self, project_id: str, from_status_id: str, to_status_id: str
    ) -> bool:
        return await self._provider.is_transition_allowed(
            project_id=project_id,
            from_status_id=from_status_id,
            to_status_id=to_status_id,
        )

    async def get_columns(self, project_id: str) -> list[dict[str, Any]]:
        return await self._provider.get_columns(project_id)
