from __future__ import annotations

from datetime import date

from app.core.logging import get_logger
from app.context.analytics.application.ports.integration.inboard.sprint_port import (
    SprintMeta,
    SprintPort,
)
from app.context.project.application.dto.sprint_dto import SprintDTO
from app.context.project.application.ports.integration.outboard.sprint_provider import (
    SprintProvider,
)


class SprintAdapter(SprintPort):
    """Inboard ``SprintPort`` Analytics BC. Делегирует в outboard Project BC."""

    def __init__(self, sprint_provider: SprintProvider) -> None:
        self._provider = sprint_provider

    async def get_sprint_meta(self, sprint_id: str) -> SprintMeta | None:
        dto = await self._provider.get_sprint(sprint_id=sprint_id)
        if dto is None:
            return None
        return _to_meta(dto)

    async def get_active_sprint_meta(self, project_id: str) -> SprintMeta | None:
        dto = await self._provider.get_active_sprint(project_id=project_id)
        if dto is None:
            return None
        return _to_meta(dto)


def _to_meta(dto: SprintDTO) -> SprintMeta:
    sprint_start, sprint_end = _parse_range(dto.date_range)
    return SprintMeta(
        id=dto.id,
        project_id=dto.project_id,
        name=dto.name,
        status=dto.status,
        sprint_start=sprint_start,
        sprint_end=sprint_end,
    )


logger = get_logger(__name__)


def _parse_range(raw: dict | None) -> tuple[date | None, date | None]:
    if not raw:
        return None, None
    if not isinstance(raw, dict):
        logger.warning("Unexpected date_range structure", raw=raw)
        return None, None
    if "start" not in raw and "end" not in raw:
        logger.warning("Unexpected date_range structure", raw=raw)
    start = _parse_date(raw.get("start"))
    end = _parse_date(raw.get("end"))
    return start, end


def _parse_date(value: object) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None
