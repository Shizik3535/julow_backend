from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.dto.task_template_dto import TaskTemplateDTO
from app.context.task.domain.exceptions.task_template_exceptions import TaskTemplateNotFoundException
from app.context.task.domain.repositories.task_template_repository import TaskTemplateRepository


class GetTaskTemplateQuery(BaseQuery):
    """
    Запрос шаблона задачи по ID.

    Атрибуты:
        template_id: Идентификатор шаблона.
    """

    template_id: str


class GetTaskTemplateHandler(BaseQueryHandler[GetTaskTemplateQuery, TaskTemplateDTO]):
    """Обработчик получения шаблона задачи по ID."""

    def __init__(self, template_repo: TaskTemplateRepository) -> None:
        super().__init__()
        self._template_repo = template_repo

    async def handle(self, query: GetTaskTemplateQuery) -> TaskTemplateDTO:
        template = await self._template_repo.get_by_id(Id.from_string(query.template_id))
        if template is None:
            raise TaskTemplateNotFoundException(id=query.template_id)

        return TaskTemplateDTO(
            id=str(template.id),
            name=template.name,
            description={"content": template.description.content, "format": template.description.format.value} if template.description else None,
            task_type=template.task_type.value,
            default_labels=[{"name": lb.name, "color": lb.color.hex if lb.color else None} for lb in template.default_labels],
            default_checklists=[{"id": str(cl.id), "title": cl.title} for cl in template.default_checklists],
            default_custom_fields=template.default_custom_fields,
            is_system=template.is_system,
            created_at=template.created_at,
            updated_at=template.updated_at,
        )
