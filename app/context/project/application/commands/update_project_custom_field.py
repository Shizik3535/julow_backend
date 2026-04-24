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


class UpdateProjectCustomFieldCommand(BaseCommand):
    """
    Команда обновления кастомного поля проекта.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        project_id: ID проекта.
        name: Текущее название поля (ключ поиска).
        new_name: Новое название.
        field_type: Тип поля.
        is_required: Обязательно ли поле.
        options: Варианты (для SELECT/MULTI_SELECT).
        default_value: Значение по умолчанию.
        description: Описание поля.
    """

    caller_id: str
    project_id: str
    name: str
    new_name: str | None = None
    field_type: str | None = None
    is_required: bool = False
    options: list[str] | None = None
    default_value: str | None = None
    description: str | None = None


class UpdateProjectCustomFieldHandler(BaseCommandHandler[UpdateProjectCustomFieldCommand, None]):
    """Обработчик обновления кастомного поля проекта."""


    REQUIRED_PERMISSION = "custom_fields.write"

    def __init__(self, project_repo: ProjectRepository, permission_checker: ProjectPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._project_repo = project_repo
        self._event_bus = event_bus
        self._permission_checker = permission_checker

    async def handle(self, command: UpdateProjectCustomFieldCommand) -> None:
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=Id.from_string(command.project_id),
            permission=self.REQUIRED_PERMISSION,
        )
        project = await self._project_repo.get_by_id(Id.from_string(command.project_id))
        if project is None:
            raise ProjectNotFoundException(command.project_id)

        existing = next((f for f in project.custom_field_definitions if f.name == command.name), None)
        if existing is None:
            from app.context.project.domain.exceptions.custom_field_exceptions import CustomFieldDefinitionNotFoundException
            raise CustomFieldDefinitionNotFoundException(name=command.name)

        new_def = CustomFieldDefinition(
            name=command.new_name or existing.name,
            field_type=CustomFieldType(command.field_type) if command.field_type else existing.field_type,
            is_required=command.is_required,
            options=command.options if command.options is not None else existing.options,
            default_value=command.default_value if command.default_value is not None else existing.default_value,
            description=command.description if command.description is not None else existing.description,
        )
        project.update_custom_field(command.name, new_def)
        await self._project_repo.update(project)
        await self._event_bus.publish_all(project.clear_domain_events())
