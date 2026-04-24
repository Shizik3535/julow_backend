from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.profile.application.exceptions.profile_app_exceptions import InvalidStartPageAppException
from app.context.profile.application.ports.navigation.start_page_registry_port import StartPageRegistryPort
from app.context.profile.domain.repositories.user_profile_repository import UserProfileRepository
from app.context.profile.domain.exceptions.profile_exceptions import ProfileNotFoundException
from app.context.profile.domain.value_objects.navigation_settings import NavigationSettings
from app.context.profile.domain.value_objects.start_page import StartPage


class UpdateNavigationCommand(BaseCommand):
    """
    Команда обновления настроек навигации.

    Атрибуты:
        user_id: ID пользователя.
        start_page: Идентификатор стартовой страницы (например dashboard, my_tasks).
    """

    user_id: str
    start_page: str = "dashboard"


class UpdateNavigationHandler(BaseCommandHandler[UpdateNavigationCommand, None]):
    """
    Обработчик обновления настроек навигации.

    Валидирует start_page через StartPageRegistryPort,
    создаёт VO NavigationSettings и вызывает update_navigation.
    """

    def __init__(
        self,
        profile_repo: UserProfileRepository,
        start_page_registry: StartPageRegistryPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._profile_repo = profile_repo
        self._start_page_registry = start_page_registry
        self._event_bus = event_bus

    async def handle(self, command: UpdateNavigationCommand) -> None:
        profile = await self._profile_repo.get_by_user_id(Id.from_string(command.user_id))
        if profile is None:
            raise ProfileNotFoundException(command.user_id)

        is_registered = await self._start_page_registry.is_registered(command.start_page)
        if not is_registered:
            raise InvalidStartPageAppException(command.start_page)

        settings = NavigationSettings(
            start_page=StartPage(command.start_page),
        )

        profile.update_navigation(settings)
        await self._profile_repo.update(profile)

        await self._event_bus.publish_all(profile.clear_domain_events())
