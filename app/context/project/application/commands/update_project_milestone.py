from __future__ import annotations

from datetime import date

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.rich_text_vo import RichText
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)


class UpdateProjectMilestoneCommand(BaseCommand):
    """
    Команда обновления milestone проекта.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        project_id: ID проекта.
        milestone_id: ID milestone.
        name: Название milestone.
        due_date: Дедлайн (ISO).
        description_content: Контент описания.
        description_format: Формат описания.
    """

    caller_id: str
    project_id: str
    milestone_id: str
    name: str | None = None
    due_date: str | None = None
    description_content: str | None = None
    description_format: str | None = None


class UpdateProjectMilestoneHandler(BaseCommandHandler[UpdateProjectMilestoneCommand, None]):
    """Обработчик обновления milestone проекта."""


    REQUIRED_PERMISSION = "milestones.write"

    def __init__(self, project_repo: ProjectRepository, permission_checker: ProjectPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._project_repo = project_repo
        self._event_bus = event_bus
        self._permission_checker = permission_checker

    async def handle(self, command: UpdateProjectMilestoneCommand) -> None:
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=Id.from_string(command.project_id),
            permission=self.REQUIRED_PERMISSION,
        )
        project = await self._project_repo.get_by_id(Id.from_string(command.project_id))
        if project is None:
            raise ProjectNotFoundException(command.project_id)

        kwargs: dict = {}
        if command.name is not None:
            kwargs["name"] = command.name
        if command.due_date is not None:
            kwargs["due_date"] = date.fromisoformat(command.due_date)
        if command.description_content is not None:
            from app.shared.domain.value_objects.rich_text_format import RichTextFormat
            fmt = RichTextFormat(command.description_format) if command.description_format else RichTextFormat.MARKDOWN
            kwargs["description"] = RichText(content=command.description_content, format=fmt)

        project.update_milestone(Id.from_string(command.milestone_id), **kwargs)
        await self._project_repo.update(project)
        await self._event_bus.publish_all(project.clear_domain_events())
