from __future__ import annotations

from datetime import date

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.rich_text_vo import RichText
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.context.project.domain.value_objects.category import Category
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)


class UpdateProjectInfoCommand(BaseCommand):
    """
    Команда обновления информации проекта.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        project_id: ID проекта.
        name: Новое название.
        description_content: Контент описания.
        description_format: Формат описания (MARKDOWN, WYSIWYG).
        icon: Иконка.
        color: Цвет (hex).
        category_name: Название категории.
        category_color: Цвет категории (hex).
        start_date: Дата начала (ISO).
        deadline: Дедлайн (ISO).
    """

    caller_id: str
    project_id: str
    name: str | None = None
    description_content: str | None = None
    description_format: str | None = None
    icon: str | None = None
    color: str | None = None
    category_name: str | None = None
    category_color: str | None = None
    start_date: str | None = None
    deadline: str | None = None


class UpdateProjectInfoHandler(BaseCommandHandler[UpdateProjectInfoCommand, None]):
    """Обработчик обновления информации проекта."""


    REQUIRED_PERMISSION = "project.settings.write"

    def __init__(self, project_repo: ProjectRepository, permission_checker: ProjectPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._project_repo = project_repo
        self._event_bus = event_bus
        self._permission_checker = permission_checker

    async def handle(self, command: UpdateProjectInfoCommand) -> None:
        project_id = Id.from_string(command.project_id)
        project = await self._project_repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundException(command.project_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=project_id,
            permission=self.REQUIRED_PERMISSION,
        )

        description: RichText | None = None
        if command.description_content is not None:
            from app.shared.domain.value_objects.rich_text_format import RichTextFormat
            fmt = RichTextFormat(command.description_format) if command.description_format else RichTextFormat.MARKDOWN
            description = RichText(content=command.description_content, format=fmt)

        color = Color(command.color) if command.color else None

        category: Category | None = None
        if command.category_name is not None:
            cat_color = Color(command.category_color) if command.category_color else None
            category = Category(name=command.category_name, color=cat_color)

        start_date = date.fromisoformat(command.start_date) if command.start_date else None
        deadline = date.fromisoformat(command.deadline) if command.deadline else None

        project.update_info(
            name=command.name,
            description=description,
            icon=command.icon,
            color=color,
            category=category,
            start_date=start_date,
            deadline=deadline,
        )
        await self._project_repo.update(project)
        await self._event_bus.publish_all(project.clear_domain_events())
