from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url
from app.context.profile.domain.repositories.user_profile_repository import UserProfileRepository
from app.context.profile.domain.exceptions.profile_exceptions import ProfileNotFoundException


class AddSocialLinkCommand(BaseCommand):
    """
    Команда добавления социальной ссылки.

    Атрибуты:
        user_id: ID пользователя.
        platform: Название платформы (например github, linkedin).
        url: URL профиля на платформе.
        display_name: Отображаемое имя (опционально).
    """

    user_id: str
    platform: str
    url: str
    display_name: str | None = None


class AddSocialLinkHandler(BaseCommandHandler[AddSocialLinkCommand, None]):
    """
    Обработчик добавления социальной ссылки.

    Загружает профиль, вызывает add_social_link, сохраняет.
    """

    def __init__(self, profile_repo: UserProfileRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._profile_repo = profile_repo
        self._event_bus = event_bus

    async def handle(self, command: AddSocialLinkCommand) -> None:
        profile = await self._profile_repo.get_by_user_id(Id.from_string(command.user_id))
        if profile is None:
            raise ProfileNotFoundException(command.user_id)

        profile.add_social_link(
            platform=command.platform,
            url=Url(command.url),
            display_name=command.display_name,
        )
        await self._profile_repo.update(profile)

        await self._event_bus.publish_all(profile.clear_domain_events())
