from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.timetracking.application.dto.mappers import time_entry_to_dto
from app.context.timetracking.application.dto.time_entry_dto import TimeEntryDTO
from app.context.timetracking.domain.repositories.time_entry_repository import (
    TimeEntryRepository,
)


class GetRunningTimerQuery(BaseQuery):
    """Запрос: текущий запущенный/приостановленный таймер пользователя."""

    caller_id: str


class GetRunningTimerHandler(BaseQueryHandler[GetRunningTimerQuery, TimeEntryDTO | None]):
    """Возвращает активный таймер пользователя или None."""

    def __init__(self, time_entry_repo: TimeEntryRepository) -> None:
        super().__init__()
        self._repo = time_entry_repo

    async def handle(self, query: GetRunningTimerQuery) -> TimeEntryDTO | None:
        entry = await self._repo.get_running_timer(Id.from_string(query.caller_id))
        if entry is None:
            return None
        return time_entry_to_dto(entry)
