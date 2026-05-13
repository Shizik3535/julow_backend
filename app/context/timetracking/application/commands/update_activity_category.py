from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.id_vo import Id

from app.context.timetracking.application.dto.activity_category_dto import ActivityCategoryDTO
from app.context.timetracking.application.dto.mappers import category_to_dto
from app.context.timetracking.application.ports.authorization.timetracking_permission_checker_port import (
    TimeTrackingPermissionCheckerPort,
)
from app.context.timetracking.domain.exceptions.category_exceptions import (
    ActivityCategoryNotFoundException,
    CannotUpdateSystemCategoryException,
    DuplicateActivityCategoryException,
)
from app.context.timetracking.domain.repositories.activity_category_repository import (
    ActivityCategoryRepository,
)


class UpdateActivityCategoryCommand(BaseCommand):
    """Команда обновления категории деятельности."""

    caller_id: str
    category_id: str
    name: str | None = None
    color: str | None = None
    description: str | None = None


class UpdateActivityCategoryHandler(
    BaseCommandHandler[UpdateActivityCategoryCommand, ActivityCategoryDTO]
):
    """Обновление категории. Системные категории — частичное обновление допускается."""

    REQUIRED_PERMISSION = "time.admin"

    def __init__(
        self,
        category_repo: ActivityCategoryRepository,
        permission_checker: TimeTrackingPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = category_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: UpdateActivityCategoryCommand) -> ActivityCategoryDTO:
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
            # Системные категории (workspace_id=None) нельзя редактировать
            # через workspace-уровневые права — требуется platform-admin.
            # В MVP запрещаем редактирование системных категорий полностью.
            raise CannotUpdateSystemCategoryException()

        if (
            command.name is not None
            and command.name != category.name
            and category.workspace_id is not None
        ):
            existing = await self._repo.get_by_name(command.name, category.workspace_id)
            if (
                existing is not None
                and existing.id != category.id
            ):
                raise DuplicateActivityCategoryException(name=command.name)

        category.update(
            name=command.name,
            color=Color(value=command.color) if command.color else None,
            description=command.description,
        )
        await self._repo.update(category)
        await self._event_bus.publish_all(category.clear_domain_events())
        return category_to_dto(category)
