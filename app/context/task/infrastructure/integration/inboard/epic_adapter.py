from __future__ import annotations

from typing import Any

from app.context.project.application.ports.integration.outboard.epic_provider import (
    EpicProvider,
)
from app.context.task.application.ports.integration.inboard.epic_port import (
    EpicPort,
)


class EpicAdapter(EpicPort):
    """
    Реализация inboard-порта EpicPort для Task BC.

    Делегирует получение данных эпиков в outboard-порт
    Project BC (EpicProvider).
    """

    def __init__(self, epic_provider: EpicProvider) -> None:
        self._provider = epic_provider

    async def epic_exists(self, epic_id: str) -> bool:
        return await self._provider.epic_exists(epic_id)

    async def get_epic(self, epic_id: str) -> dict[str, Any] | None:
        dto = await self._provider.get_epic(epic_id)
        if dto is None:
            return None
        return {"id": dto.id, "name": dto.name, "status": getattr(dto, "status", None)}
