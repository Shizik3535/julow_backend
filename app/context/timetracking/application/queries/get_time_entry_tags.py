from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.timetracking.application.dto.mappers import tag_to_dto
from app.context.timetracking.application.dto.time_entry_tag_dto import TimeEntryTagListDTO
from app.context.timetracking.application.ports.authorization.timetracking_permission_checker_port import (
    TimeTrackingPermissionCheckerPort,
)
from app.context.timetracking.domain.repositories.time_entry_tag_repository import (
    TimeEntryTagRepository,
)


class GetTimeEntryTagsQuery(BaseQuery):
    """Запрос: теги записей времени в workspace."""

    caller_id: str
    workspace_id: str


class GetTimeEntryTagsHandler(BaseQueryHandler[GetTimeEntryTagsQuery, TimeEntryTagListDTO]):
    """Получить теги workspace. Требует time.read."""

    REQUIRED_PERMISSION = "time.read"

    def __init__(
        self,
        tag_repo: TimeEntryTagRepository,
        permission_checker: TimeTrackingPermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._repo = tag_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetTimeEntryTagsQuery) -> TimeEntryTagListDTO:
        await self._permission_checker.require_permission(
            user_id=query.caller_id,
            workspace_id=query.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )
        tags = await self._repo.get_by_workspace(Id.from_string(query.workspace_id))
        items = [tag_to_dto(t) for t in tags]
        return TimeEntryTagListDTO(items=items, total=len(items))
