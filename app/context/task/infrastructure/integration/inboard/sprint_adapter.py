from __future__ import annotations

from typing import Any

from app.context.project.application.ports.integration.outboard.sprint_provider import (
    SprintProvider,
)
from app.context.task.application.ports.integration.inboard.sprint_port import (
    SprintPort,
)


class SprintAdapter(SprintPort):
    """
    Реализация inboard-порта SprintPort для Task BC.

    Делегирует получение данных спринтов в outboard-порт
    Project BC (SprintProvider).
    """

    def __init__(self, sprint_provider: SprintProvider) -> None:
        self._provider = sprint_provider

    async def sprint_exists(self, sprint_id: str) -> bool:
        return await self._provider.sprint_exists(sprint_id)

    async def get_sprint(self, sprint_id: str) -> dict[str, Any] | None:
        dto = await self._provider.get_sprint(sprint_id)
        if dto is None:
            return None
        return {"id": dto.id, "name": dto.name, "status": getattr(dto, "status", None)}

    async def get_active_sprint(self, project_id: str) -> dict[str, Any] | None:
        dto = await self._provider.get_active_sprint(project_id)
        if dto is None:
            return None
        return {"id": dto.id, "name": dto.name, "status": getattr(dto, "status", None)}
