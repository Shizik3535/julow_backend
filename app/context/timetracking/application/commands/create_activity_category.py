from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.id_vo import Id

from app.context.timetracking.application.dto.activity_category_dto import ActivityCategoryDTO
from app.context.timetracking.application.dto.mappers import category_to_dto
from app.context.timetracking.application.exceptions.timetracking_app_exceptions import (
    TimeEntryWorkspaceNotFoundException,
)
from app.context.timetracking.application.ports.authorization.timetracking_permission_checker_port import (
    TimeTrackingPermissionCheckerPort,
)
from app.context.timetracking.application.ports.integration.inboard.workspace_port import (
    WorkspacePort,
)
from app.context.timetracking.domain.aggregates.activity_category import ActivityCategory
from app.context.timetracking.domain.exceptions.category_exceptions import (
    DuplicateActivityCategoryException,
)
from app.context.timetracking.domain.repositories.activity_category_repository import (
    ActivityCategoryRepository,
)


class CreateActivityCategoryCommand(BaseCommand):
    """Команда создания пользовательской категории деятельности."""

    caller_id: str
    workspace_id: str
    name: str
    color: str | None = None
    description: str | None = None


class CreateActivityCategoryHandler(
    BaseCommandHandler[CreateActivityCategoryCommand, ActivityCategoryDTO]
):
    """Создание пользовательской категории (is_system=False)."""

    REQUIRED_PERMISSION = "time.admin"

    def __init__(
        self,
        category_repo: ActivityCategoryRepository,
        permission_checker: TimeTrackingPermissionCheckerPort,
        workspace_port: WorkspacePort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = category_repo
        self._permission_checker = permission_checker
        self._workspace_port = workspace_port
        self._event_bus = event_bus

    async def handle(self, command: CreateActivityCategoryCommand) -> ActivityCategoryDTO:
        if not await self._workspace_port.workspace_exists(command.workspace_id):
            raise TimeEntryWorkspaceNotFoundException(command.workspace_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=command.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )

        workspace_id = Id.from_string(command.workspace_id)
        existing = await self._repo.get_by_name(command.name, workspace_id)
        if existing is not None:
            raise DuplicateActivityCategoryException(name=command.name)
        # Проверяем, нет ли системной категории с таким же именем
        existing_system = await self._repo.get_by_name(command.name, workspace_id=None)
        if existing_system is not None:
            raise DuplicateActivityCategoryException(name=command.name)

        category = ActivityCategory.create_custom(
            workspace_id=workspace_id,
            name=command.name,
            color=Color(value=command.color) if command.color else None,
            description=command.description,
        )
        await self._repo.add(category)
        await self._event_bus.publish_all(category.clear_domain_events())
        return category_to_dto(category)
