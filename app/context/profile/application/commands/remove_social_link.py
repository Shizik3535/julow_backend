from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.profile.domain.repositories.user_profile_repository import UserProfileRepository
from app.context.profile.domain.exceptions.profile_exceptions import ProfileNotFoundException


class RemoveSocialLinkCommand(BaseCommand):
    """
    Команда удаления социальной ссылки.

    Атрибуты:
        user_id: ID пользователя.
        platform: Название платформы для удаления.
    """

    user_id: str
    platform: str


class RemoveSocialLinkHandler(BaseCommandHandler[RemoveSocialLinkCommand, None]):
    """
    Обработчик удаления социальной ссылки.

    Загружает профиль, вызывает remove_social_link, сохраняет.
    """

    def __init__(self, profile_repo: UserProfileRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._profile_repo = profile_repo
        self._event_bus = event_bus

    async def handle(self, command: RemoveSocialLinkCommand) -> None:
        profile = await self._profile_repo.get_by_user_id(Id.from_string(command.user_id))
        if profile is None:
            raise ProfileNotFoundException(command.user_id)

        profile.remove_social_link(platform=command.platform)
        await self._profile_repo.update(profile)

        await self._event_bus.publish_all(profile.clear_domain_events())
