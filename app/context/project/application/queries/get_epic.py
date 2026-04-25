from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.epic_dto import EpicDTO
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)
from app.context.project.application.queries.get_epics_by_project import GetEpicsByProjectHandler
from app.context.project.domain.exceptions.epic_exceptions import EpicNotFoundException
from app.context.project.domain.repositories.epic_repository import EpicRepository


class GetEpicQuery(BaseQuery):
    """Запрос получения эпика по ID."""

    caller_id: str
    epic_id: str


class GetEpicHandler(BaseQueryHandler[GetEpicQuery, EpicDTO]):
    """Обработчик получения эпика по ID."""

    REQUIRED_PERMISSION = "epics.read"

    def __init__(self, epic_repo: EpicRepository, permission_checker: ProjectPermissionCheckerPort) -> None:
        super().__init__()
        self._epic_repo = epic_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetEpicQuery) -> EpicDTO:
        epic = await self._epic_repo.get_by_id(Id.from_string(query.epic_id))
        if epic is None:
            raise EpicNotFoundException(query.epic_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(query.caller_id),
            project_id=epic.project_id,
            permission=self.REQUIRED_PERMISSION,
        )
        return GetEpicsByProjectHandler._to_dto(epic)
