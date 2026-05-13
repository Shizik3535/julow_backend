from __future__ import annotations

from datetime import date

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.timetracking.application.dto.mappers import time_entry_to_dto
from app.context.timetracking.application.dto.time_entry_dto import TimeEntryListDTO
from app.context.timetracking.domain.repositories.time_entry_repository import (
    TimeEntryRepository,
)


class GetMyTimeEntriesQuery(BaseQuery):
    """Запрос: записи времени текущего пользователя (опционально за дату)."""

    caller_id: str
    entry_date: str | None = None


class GetMyTimeEntriesHandler(BaseQueryHandler[GetMyTimeEntriesQuery, TimeEntryListDTO]):
    """Записи времени пользователя; нет проверки workspace permissions."""

    def __init__(self, time_entry_repo: TimeEntryRepository) -> None:
        super().__init__()
        self._repo = time_entry_repo

    async def handle(self, query: GetMyTimeEntriesQuery) -> TimeEntryListDTO:
        user_id = Id.from_string(query.caller_id)
        if query.entry_date:
            entries = await self._repo.get_by_user_and_date(
                user_id, date.fromisoformat(query.entry_date)
            )
        else:
            entries = await self._repo.get_by_user(user_id)
        items = [time_entry_to_dto(e) for e in entries]
        return TimeEntryListDTO(items=items, total=len(items))
