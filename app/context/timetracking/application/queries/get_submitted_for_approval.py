from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.timetracking.application.dto.mappers import time_entry_to_dto
from app.context.timetracking.application.dto.time_entry_dto import TimeEntryListDTO
from app.context.timetracking.application.ports.authorization.timetracking_permission_checker_port import (
    TimeTrackingPermissionCheckerPort,
)
from app.context.timetracking.domain.repositories.time_entry_repository import (
    TimeEntryRepository,
)


class GetSubmittedForApprovalQuery(BaseQuery):
    """Запрос: записи времени, ожидающие утверждения, в workspace."""

    caller_id: str
    workspace_id: str


class GetSubmittedForApprovalHandler(
    BaseQueryHandler[GetSubmittedForApprovalQuery, TimeEntryListDTO]
):
    """Записи в статусе SUBMITTED. Требует time.approve."""

    REQUIRED_PERMISSION = "time.approve"

    def __init__(
        self,
        time_entry_repo: TimeEntryRepository,
        permission_checker: TimeTrackingPermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._repo = time_entry_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetSubmittedForApprovalQuery) -> TimeEntryListDTO:
        await self._permission_checker.require_permission(
            user_id=query.caller_id,
            workspace_id=query.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )
        entries = await self._repo.get_submitted_for_approval(Id.from_string(query.workspace_id))
        items = [time_entry_to_dto(e) for e in entries]
        return TimeEntryListDTO(items=items, total=len(items))
