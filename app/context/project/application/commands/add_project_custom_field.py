from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.context.project.domain.value_objects.custom_field_definition import CustomFieldDefinition
from app.context.project.domain.value_objects.custom_field_type import CustomFieldType
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)


class AddProjectCustomFieldCommand(BaseCommand):
    """
    Команда добавления кастомного поля проекта.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        project_id: ID проекта.
        name: Название поля.
        field_type: Тип поля (TEXT, NUMBER, DATE, SELECT, ...).
        is_required: Обязательно ли поле.
        options: Варианты (для SELECT/MULTI_SELECT).
        default_value: Значение по умолчанию.
        description: Описание поля.
    """

    caller_id: str
    project_id: str
    name: str
    field_type: str
    is_required: bool = False
    options: list[str] | None = None
    default_value: str | None = None
    description: str | None = None


class AddProjectCustomFieldHandler(BaseCommandHandler[AddProjectCustomFieldCommand, None]):
    """Обработчик добавления кастомного поля проекта."""


    REQUIRED_PERMISSION = "custom_fields.write"

    def __init__(self, project_repo: ProjectRepository, permission_checker: ProjectPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._project_repo = project_repo
        self._event_bus = event_bus
        self._permission_checker = permission_checker

    async def handle(self, command: AddProjectCustomFieldCommand) -> None:
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=Id.from_string(command.project_id),
            permission=self.REQUIRED_PERMISSION,
        )
        project = await self._project_repo.get_by_id(Id.from_string(command.project_id))
        if project is None:
            raise ProjectNotFoundException(command.project_id)

        definition = CustomFieldDefinition(
            name=command.name,
            field_type=CustomFieldType(command.field_type),
            is_required=command.is_required,
            options=command.options,
            default_value=command.default_value,
            description=command.description,
        )
        project.add_custom_field(definition)
        await self._project_repo.update(project)
        await self._event_bus.publish_all(project.clear_domain_events())
