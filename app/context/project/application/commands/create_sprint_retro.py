from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.exceptions.sprint_exceptions import SprintNotFoundException
from app.context.project.domain.repositories.retro_template_repository import RetroTemplateRepository
from app.context.project.domain.repositories.sprint_repository import SprintRepository
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)


class CreateSprintRetroCommand(BaseCommand):
    """
    Команда создания ретроспективы спринта.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        sprint_id: ID спринта.
        template_id: ID шаблона ретроспективы.
    """

    caller_id: str
    sprint_id: str
    template_id: str


class CreateSprintRetroHandler(BaseCommandHandler[CreateSprintRetroCommand, None]):
    """
    Обработчик создания ретроспективы.

    Загружает RetroTemplate и передаёт данные в Sprint.create_retro.
    """


    REQUIRED_PERMISSION = "sprints.retro.write"

    def __init__(
        self,
        sprint_repo: SprintRepository,
        retro_template_repo: RetroTemplateRepository,
        permission_checker: ProjectPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._sprint_repo = sprint_repo
        self._retro_template_repo = retro_template_repo
        self._event_bus = event_bus
        self._permission_checker = permission_checker
    async def handle(self, command: CreateSprintRetroCommand) -> None:
        sprint = await self._sprint_repo.get_by_id(Id.from_string(command.sprint_id))
        if sprint is None:
            raise SprintNotFoundException(command.sprint_id)


        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=sprint.project_id,
            permission=self.REQUIRED_PERMISSION,
        )
        template = await self._retro_template_repo.get_by_id(Id.from_string(command.template_id))
        if template is None:
            raise ValueError(f"Шаблон ретроспективы не найден: {command.template_id}")

        sprint.create_retro(template_name=template.name, sections=template.sections)
        await self._sprint_repo.update(sprint)
        await self._event_bus.publish_all(sprint.clear_domain_events())
