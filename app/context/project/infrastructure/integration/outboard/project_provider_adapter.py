from __future__ import annotations

from app.context.project.application.dto.project_dto import ProjectDTO
from app.context.project.application.ports.integration.outboard.project_provider import (
    ProjectProvider,
)
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.shared.domain.value_objects.id_vo import Id


class ProjectProviderAdapter(ProjectProvider):
    """
    Реализация outboard-порта ProjectProvider.

    Делегирует в ProjectRepository для предоставления данных проекта другим BC.
    """

    def __init__(self, repo: ProjectRepository) -> None:
        self._repo = repo

    async def get_project(self, project_id: str) -> ProjectDTO | None:
        project = await self._repo.get_by_id(Id.from_string(project_id))
        if project is None:
            return None
        return self._to_dto(project)

    async def project_exists(self, project_id: str) -> bool:
        project = await self._repo.get_by_id(Id.from_string(project_id))
        return project is not None

    async def get_projects_by_workspace(self, workspace_id: str) -> list[ProjectDTO]:
        projects = await self._repo.get_by_workspace(Id.from_string(workspace_id))
        return [self._to_dto(p) for p in projects]

    @staticmethod
    def _to_dto(project) -> ProjectDTO:
        from app.shared.domain.value_objects.rich_text_format import RichTextFormat

        description = None
        if project.description is not None:
            description = {
                "content": project.description.content,
                "format": project.description.format.value,
            }

        category = None
        if project.category is not None:
            category = {
                "name": project.category.name,
                "color": str(project.category.color) if project.category.color else None,
            }

        methodology_capabilities = {}
        if project.methodology_capabilities is not None:
            mc = project.methodology_capabilities
            methodology_capabilities = {
                "has_sprints": mc.has_sprints,
                "has_backlog": mc.has_backlog,
                "has_milestones": mc.has_milestones,
                "has_epics": mc.has_epics,
                "has_wip_limits": mc.has_wip_limits,
                "has_velocity": mc.has_velocity,
                "has_retros": mc.has_retros,
                "has_burndown": mc.has_burndown,
            }

        return ProjectDTO(
            id=str(project.id),
            workspace_id=str(project.workspace_id) if project.workspace_id else None,
            name=project.name,
            description=description,
            icon=project.icon,
            color=str(project.color) if project.color else None,
            category=category,
            methodology=project.methodology.value,
            methodology_capabilities=methodology_capabilities,
            visibility=project.visibility.value,
            status=project.status.value,
            owner_ids=[str(oid) for oid in project.owner_ids],
            start_date=str(project.start_date) if project.start_date else None,
            deadline=str(project.deadline) if project.deadline else None,
            milestones=[
                {
                    "id": str(m.id),
                    "name": m.name,
                    "status": m.status.value,
                    "due_date": str(m.due_date),
                }
                for m in project.milestones
            ],
            custom_field_definitions=[
                {
                    "name": f.name,
                    "field_type": f.field_type.value,
                    "is_required": f.is_required,
                }
                for f in project.custom_field_definitions
            ],
            created_at=project.created_at,
            updated_at=project.updated_at,
        )
