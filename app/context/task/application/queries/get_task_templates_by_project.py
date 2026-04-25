from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.dto.task_template_dto import TaskTemplateDTO, TaskTemplateListDTO
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
from app.context.task.domain.repositories.task_template_repository import TaskTemplateRepository


class GetTaskTemplatesByProjectQuery(BaseQuery):
    """
    Запрос шаблонов задач проекта.

    Атрибуты:
        project_id: ID проекта.
    """

    caller_id: str
    project_id: str


class GetTaskTemplatesByProjectHandler(BaseQueryHandler[GetTaskTemplatesByProjectQuery, TaskTemplateListDTO]):
    """Обработчик получения шаблонов задач проекта."""

    REQUIRED_PERMISSION = "tasks.read"

    def __init__(self, template_repo: TaskTemplateRepository, permission_checker: TaskPermissionCheckerPort) -> None:
        super().__init__()
        self._template_repo = template_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetTaskTemplatesByProjectQuery) -> TaskTemplateListDTO:
        await self._permission_checker.require_permission(
            user_id=query.caller_id,
            project_id=query.project_id,
            permission=self.REQUIRED_PERMISSION,
        )
        templates = await self._template_repo.get_by_project(Id.from_string(query.project_id))
        items = [
            TaskTemplateDTO(
                id=str(t.id),
                name=t.name,
                description={"content": t.description.content, "format": t.description.format.value} if t.description else None,
                task_type=t.task_type.value,
                default_labels=[{"name": lb.name, "color": lb.color.hex if lb.color else None} for lb in t.default_labels],
                default_checklists=[{"id": str(cl.id), "title": cl.title} for cl in t.default_checklists],
                default_custom_fields=t.default_custom_fields,
                is_system=t.is_system,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
            for t in templates
        ]
        return TaskTemplateListDTO(items=items, total=len(items))
