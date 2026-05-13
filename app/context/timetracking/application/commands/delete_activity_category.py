from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.timetracking.application.ports.authorization.timetracking_permission_checker_port import (
    TimeTrackingPermissionCheckerPort,
)
from app.context.timetracking.domain.exceptions.category_exceptions import (
    ActivityCategoryInUseException,
    ActivityCategoryNotFoundException,
)
from app.context.timetracking.domain.repositories.activity_category_repository import (
    ActivityCategoryRepository,
)
from app.context.timetracking.domain.repositories.time_entry_repository import (
    TimeEntryRepository,
)


class DeleteActivityCategoryCommand(BaseCommand):
    """Команда удаления категории деятельности (soft delete)."""

    caller_id: str
    category_id: str


class DeleteActivityCategoryHandler(BaseCommandHandler[DeleteActivityCategoryCommand, None]):
    """Удаление категории. Системные нельзя; используемые в записях — нельзя."""

    REQUIRED_PERMISSION = "time.admin"

    def __init__(
        self,
        category_repo: ActivityCategoryRepository,
        time_entry_repo: TimeEntryRepository,
        permission_checker: TimeTrackingPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = category_repo
        self._time_entry_repo = time_entry_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: DeleteActivityCategoryCommand) -> None:
        category = await self._repo.get_by_id(Id.from_string(command.category_id))
        if category is None:
            raise ActivityCategoryNotFoundException(id=command.category_id)
        if category.workspace_id is not None:
            await self._permission_checker.require_permission(
                user_id=command.caller_id,
                workspace_id=str(category.workspace_id),
                permission=self.REQUIRED_PERMISSION,
            )
        else:
            # Системные категории (workspace_id=None) нельзя удалить
            # через workspace-уровневые права.
            raise CannotDeleteSystemCategoryException(name=category.name)

        # Проверка использования
        in_use = await self._time_entry_repo.get_by_category(category.id)
        if in_use:
            raise ActivityCategoryInUseException()

        category.mark_deleted()  # выбросит CannotDeleteSystemCategoryException если is_system
        events = category.clear_domain_events()
        await self._repo.update(category)
        await self._event_bus.publish_all(events)
