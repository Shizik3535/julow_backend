from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.timetracking.application.dto.activity_category_dto import (
    ActivityCategoryListDTO,
)
from app.context.timetracking.application.dto.mappers import category_to_dto
from app.context.timetracking.application.ports.authorization.timetracking_permission_checker_port import (
    TimeTrackingPermissionCheckerPort,
)
from app.context.timetracking.domain.repositories.activity_category_repository import (
    ActivityCategoryRepository,
)


class GetActivityCategoriesQuery(BaseQuery):
    """Запрос: категории деятельности (системные + workspace-специфичные)."""

    caller_id: str
    workspace_id: str
    include_system: bool = True


class GetActivityCategoriesHandler(
    BaseQueryHandler[GetActivityCategoriesQuery, ActivityCategoryListDTO]
):
    """Получить категории. Требует time.read в workspace."""

    REQUIRED_PERMISSION = "time.read"

    def __init__(
        self,
        category_repo: ActivityCategoryRepository,
        permission_checker: TimeTrackingPermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._repo = category_repo
        self._permission_checker = permission_checker

    async def handle(
        self, query: GetActivityCategoriesQuery
    ) -> ActivityCategoryListDTO:
        await self._permission_checker.require_permission(
            user_id=query.caller_id,
            workspace_id=query.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )
        # get_by_workspace уже включает системные категории через OR is_system=True
        result = await self._repo.get_by_workspace(Id.from_string(query.workspace_id))
        if not query.include_system:
            result = [c for c in result if not c.is_system]
        items = [category_to_dto(c) for c in result]
        return ActivityCategoryListDTO(items=items, total=len(items))
