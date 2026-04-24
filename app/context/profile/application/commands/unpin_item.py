from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.profile.domain.repositories.user_profile_repository import UserProfileRepository
from app.context.profile.domain.exceptions.profile_exceptions import ProfileNotFoundException
from app.context.profile.domain.value_objects.pinned_target_type import PinnedTargetType


class UnpinItemCommand(BaseCommand):
    """
    Команда открепления элемента.

    Атрибуты:
        user_id: ID пользователя.
        target_type: Тип элемента (WORKSPACE, PROJECT, TASK, DASHBOARD, REPORT).
        target_id: ID элемента.
    """

    user_id: str
    target_type: str
    target_id: str


class UnpinItemHandler(BaseCommandHandler[UnpinItemCommand, None]):
    """
    Обработчик открепления элемента.

    Загружает профиль, вызывает unpin_item, сохраняет.
    """

    def __init__(self, profile_repo: UserProfileRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._profile_repo = profile_repo
        self._event_bus = event_bus

    async def handle(self, command: UnpinItemCommand) -> None:
        profile = await self._profile_repo.get_by_user_id(Id.from_string(command.user_id))
        if profile is None:
            raise ProfileNotFoundException(command.user_id)

        profile.unpin_item(
            target_type=PinnedTargetType(command.target_type),
            target_id=Id.from_string(command.target_id),
        )
        await self._profile_repo.update(profile)

        await self._event_bus.publish_all(profile.clear_domain_events())
