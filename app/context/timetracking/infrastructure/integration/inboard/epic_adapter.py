from __future__ import annotations

from app.context.project.application.ports.integration.outboard.epic_provider import EpicProvider
from app.context.timetracking.application.ports.integration.inboard.epic_port import EpicPort


class EpicAdapter(EpicPort):
    """Inboard EpicPort для TimeTracking BC. Делегирует в outboard Project BC (Epic)."""

    def __init__(self, epic_provider: EpicProvider) -> None:
        self._provider = epic_provider

    async def epic_exists(self, epic_id: str) -> bool:
        return await self._provider.epic_exists(epic_id)
