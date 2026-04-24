from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.profile.domain.repositories.user_profile_repository import UserProfileRepository
from app.context.profile.domain.exceptions.profile_exceptions import ProfileNotFoundException


class ReorderPinnedItemsCommand(BaseCommand):
    """
    Команда переупорядочивания закреплённых элементов.

    Атрибуты:
        user_id: ID пользователя.
        ordered_ids: Список target_id в желаемом порядке.
    """

    user_id: str
    ordered_ids: list[str]


class ReorderPinnedItemsHandler(BaseCommandHandler[ReorderPinnedItemsCommand, None]):
    """
    Обработчик переупорядочивания закреплённых элементов.

    Загружает профиль, вызывает reorder_pinned_items, сохраняет.
    """

    def __init__(self, profile_repo: UserProfileRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._profile_repo = profile_repo
        self._event_bus = event_bus

    async def handle(self, command: ReorderPinnedItemsCommand) -> None:
        profile = await self._profile_repo.get_by_user_id(Id.from_string(command.user_id))
        if profile is None:
            raise ProfileNotFoundException(command.user_id)

        ordered_ids = [Id.from_string(tid) for tid in command.ordered_ids]
        profile.reorder_pinned_items(ordered_ids)
        await self._profile_repo.update(profile)

        await self._event_bus.publish_all(profile.clear_domain_events())
