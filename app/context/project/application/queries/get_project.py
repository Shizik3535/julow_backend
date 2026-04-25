from __future__ import annotations

from typing import Any

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.project_dto import ProjectDTO
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)
from app.context.project.domain.aggregates.project import Project
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from app.context.project.domain.repositories.project_repository import ProjectRepository


class GetProjectQuery(BaseQuery):
    """Запрос получения проекта по ID."""

    caller_id: str
    project_id: str


class GetProjectHandler(BaseQueryHandler[GetProjectQuery, ProjectDTO]):
    """Обработчик получения проекта по ID."""

    REQUIRED_PERMISSION = "project.read"

    def __init__(self, project_repo: ProjectRepository, permission_checker: ProjectPermissionCheckerPort) -> None:
        super().__init__()
        self._project_repo = project_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetProjectQuery) -> ProjectDTO:
        project_id = Id.from_string(query.project_id)
        project = await self._project_repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundException(query.project_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(query.caller_id),
            project_id=project_id,
            permission=self.REQUIRED_PERMISSION,
        )
        return self._to_dto(project)

    @staticmethod
    def _to_dto(p: Project) -> ProjectDTO:
        milestones: list[dict[str, Any]] = []
        for m in p.milestones:
            milestones.append({
                "id": str(m.id),
                "name": m.name,
                "description": {"content": m.description.content, "format": m.description.format.value} if m.description else None,
                "status": m.status.value,
                "due_date": str(m.due_date),
                "completed_at": m.completed_at.isoformat() if m.completed_at else None,
            })

        custom_fields: list[dict[str, Any]] = []
        for cf in p.custom_field_definitions:
            custom_fields.append({
                "name": cf.name,
                "field_type": cf.field_type.value,
                "is_required": cf.is_required,
                "options": cf.options,
                "default_value": cf.default_value,
                "description": cf.description,
            })

        return ProjectDTO(
            id=str(p.id),
            workspace_id=str(p.workspace_id) if p.workspace_id else None,
            name=p.name,
            description={"content": p.description.content, "format": p.description.format.value} if p.description else None,
            icon=p.icon,
            color=str(p.color) if p.color else None,
            category={"name": p.category.name, "color": str(p.category.color) if p.category.color else None} if p.category else None,
            methodology=p.methodology.value,
            methodology_capabilities={
                "has_sprints": p.methodology_capabilities.has_sprints,
                "has_backlog": p.methodology_capabilities.has_backlog,
                "has_milestones": p.methodology_capabilities.has_milestones,
                "has_epics": p.methodology_capabilities.has_epics,
                "has_wip_limits": p.methodology_capabilities.has_wip_limits,
                "has_velocity": p.methodology_capabilities.has_velocity,
                "has_retros": p.methodology_capabilities.has_retros,
                "has_burndown": p.methodology_capabilities.has_burndown,
            },
            visibility=p.visibility.value,
            status=p.status.value,
            owner_ids=[str(oid) for oid in p.owner_ids],
            start_date=str(p.start_date) if p.start_date else None,
            deadline=str(p.deadline) if p.deadline else None,
            milestones=milestones,
            custom_field_definitions=custom_fields,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
