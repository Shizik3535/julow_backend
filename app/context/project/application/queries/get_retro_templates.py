from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.context.project.application.dto.retro_template_dto import RetroTemplateDTO, RetroTemplateListDTO
from app.context.project.domain.aggregates.retro_template import RetroTemplate
from app.context.project.domain.repositories.retro_template_repository import RetroTemplateRepository


class GetRetroTemplatesQuery(BaseQuery):
    """Запрос получения шаблонов ретроспектив."""

    pass


class GetRetroTemplatesHandler(BaseQueryHandler[GetRetroTemplatesQuery, RetroTemplateListDTO]):
    """Обработчик получения шаблонов ретроспектив."""

    def __init__(self, retro_template_repo: RetroTemplateRepository) -> None:
        super().__init__()
        self._retro_template_repo = retro_template_repo

    async def handle(self, query: GetRetroTemplatesQuery) -> RetroTemplateListDTO:
        templates = await self._retro_template_repo.get_system_templates()
        items = [self._to_dto(t) for t in templates]
        return RetroTemplateListDTO(items=items, total=len(items))

    @staticmethod
    def _to_dto(t: RetroTemplate) -> RetroTemplateDTO:
        return RetroTemplateDTO(
            id=str(t.id),
            name=t.name,
            sections=[
                {"title": s.title, "prompt": s.prompt, "item_type": s.item_type.value}
                for s in t.sections
            ],
            is_system=t.is_system,
            created_at=t.created_at,
            updated_at=t.updated_at,
        )
