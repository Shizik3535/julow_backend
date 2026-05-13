from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.timetracking.application.dto.mappers import time_entry_to_dto
from app.context.timetracking.application.dto.time_entry_dto import TimeEntryDTO
from app.context.timetracking.application.ports.authorization.timetracking_permission_checker_port import (
    TimeTrackingPermissionCheckerPort,
)
from app.context.timetracking.domain.exceptions.time_entry_exceptions import (
    TimeEntryNotFoundException,
)
from app.context.timetracking.domain.repositories.time_entry_repository import (
    TimeEntryRepository,
)


class GetTimeEntryQuery(BaseQuery):
    """Запрос получения записи времени по ID."""

    caller_id: str
    entry_id: str


class GetTimeEntryHandler(BaseQueryHandler[GetTimeEntryQuery, TimeEntryDTO]):
    """Получить запись по ID."""

    REQUIRED_PERMISSION = "time.read"

    def __init__(
        self,
        time_entry_repo: TimeEntryRepository,
        permission_checker: TimeTrackingPermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._repo = time_entry_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetTimeEntryQuery) -> TimeEntryDTO:
        entry = await self._repo.get_by_id(Id.from_string(query.entry_id))
        if entry is None:
            raise TimeEntryNotFoundException(id=query.entry_id)
        await self._permission_checker.require_permission(
            user_id=query.caller_id,
            workspace_id=str(entry.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )
        return time_entry_to_dto(entry)
