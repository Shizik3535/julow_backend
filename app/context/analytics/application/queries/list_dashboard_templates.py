from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.analytics.application.dto.dashboard_template_dto import (
    DashboardTemplateListDTO,
)
from app.context.analytics.application.dto.mappers import dashboard_template_to_dto
from app.context.analytics.domain.repositories.dashboard_template_repository import (
    DashboardTemplateRepository,
)


class ListDashboardTemplatesQuery(BaseQuery):
    """Список шаблонов: системные + workspace-specific.

    Если задан workspace_id — возвращает системные ∪ шаблоны этого workspace.
    Если нет — только системные.
    """

    caller_id: str
    workspace_id: str | None = None


class ListDashboardTemplatesHandler(
    BaseQueryHandler[ListDashboardTemplatesQuery, DashboardTemplateListDTO]
):
    def __init__(self, template_repo: DashboardTemplateRepository) -> None:
        super().__init__()
        self._repo = template_repo

    async def handle(
        self, query: ListDashboardTemplatesQuery
    ) -> DashboardTemplateListDTO:
        system = await self._repo.get_system_templates()
        items = list(system)
        if query.workspace_id is not None:
            ws = await self._repo.get_by_workspace(Id.from_string(query.workspace_id))
            items.extend(ws)
        dtos = [dashboard_template_to_dto(t) for t in items]
        return DashboardTemplateListDTO(items=dtos, total=len(dtos))
