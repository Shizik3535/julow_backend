from __future__ import annotations

from datetime import date

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.rich_text_vo import RichText
from app.context.project.domain.exceptions.epic_exceptions import EpicNotFoundException
from app.context.project.domain.repositories.epic_repository import EpicRepository
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)


class UpdateEpicCommand(BaseCommand):
    """
    Команда обновления эпика.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        epic_id: ID эпика.
        name: Название.
        description_content: Контент описания.
        description_format: Формат описания.
        owner_id: ID владельца.
        color: Цвет (hex).
        start_date: Дата начала (ISO).
        due_date: Дедлайн (ISO).
    """

    epic_id: str
    caller_id: str
    name: str | None = None
    description_content: str | None = None
    description_format: str | None = None
    owner_id: str | None = None
    color: str | None = None
    start_date: str | None = None
    due_date: str | None = None


class UpdateEpicHandler(BaseCommandHandler[UpdateEpicCommand, None]):
    """Обработчик обновления эпика."""

    REQUIRED_PERMISSION = "epics.write"

    def __init__(self, epic_repo: EpicRepository, permission_checker: ProjectPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._epic_repo = epic_repo
        self._event_bus = event_bus
        self._permission_checker = permission_checker

    async def handle(self, command: UpdateEpicCommand) -> None:
        epic = await self._epic_repo.get_by_id(Id.from_string(command.epic_id))
        if epic is None:
            raise EpicNotFoundException(command.epic_id)


        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=epic.project_id,
            permission=self.REQUIRED_PERMISSION,
        )
        description: RichText | None = None
        if command.description_content is not None:
            from app.shared.domain.value_objects.rich_text_format import RichTextFormat
            fmt = RichTextFormat(command.description_format) if command.description_format else RichTextFormat.MARKDOWN
            description = RichText(content=command.description_content, format=fmt)

        color = Color(command.color) if command.color else None
        owner_id = Id.from_string(command.owner_id) if command.owner_id else None
        start_date = date.fromisoformat(command.start_date) if command.start_date else None
        due_date = date.fromisoformat(command.due_date) if command.due_date else None

        epic.update(
            name=command.name,
            description=description,
            owner_id=owner_id,
            color=color,
            start_date=start_date,
            due_date=due_date,
        )
        await self._epic_repo.update(epic)
        await self._event_bus.publish_all(epic.clear_domain_events())
