from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.id_vo import Id
from app.context.profile.domain.repositories.user_profile_repository import UserProfileRepository
from app.context.profile.domain.exceptions.profile_exceptions import ProfileNotFoundException
from app.context.profile.domain.value_objects.appearance_settings import AppearanceSettings
from app.context.profile.domain.value_objects.custom_theme import CustomTheme
from app.context.profile.domain.value_objects.interface_density import InterfaceDensity
from app.context.profile.domain.value_objects.theme import Theme


class UpdateAppearanceCommand(BaseCommand):
    """
    Команда обновления настроек внешнего вида.

    Атрибуты:
        user_id: ID пользователя.
        theme: Тема (LIGHT, DARK, SYSTEM, CUSTOM).
        accent_color: Акцентный цвет (#RRGGBB).
        interface_density: Плотность интерфейса (COMPACT, COMFORTABLE, SPACIOUS).
        custom_theme_name: Название пользовательской темы (при theme=CUSTOM).
        custom_theme_colors: Цвета пользовательской темы {роль: #RRGGBB} (при theme=CUSTOM).
    """

    user_id: str
    theme: str = "SYSTEM"
    accent_color: str = "#6366F1"
    interface_density: str = "COMFORTABLE"
    custom_theme_name: str | None = None
    custom_theme_colors: dict[str, str] | None = None


class UpdateAppearanceHandler(BaseCommandHandler[UpdateAppearanceCommand, None]):
    """
    Обработчик обновления настроек внешнего вида.

    Создаёт VO AppearanceSettings из входных данных,
    вызывает доменный метод update_appearance.
    """

    def __init__(self, profile_repo: UserProfileRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._profile_repo = profile_repo
        self._event_bus = event_bus

    async def handle(self, command: UpdateAppearanceCommand) -> None:
        profile = await self._profile_repo.get_by_user_id(Id.from_string(command.user_id))
        if profile is None:
            raise ProfileNotFoundException(command.user_id)

        custom_theme: CustomTheme | None = None
        if command.custom_theme_name is not None and command.custom_theme_colors is not None:
            custom_theme = CustomTheme(
                name=command.custom_theme_name,
                colors={role: Color(hex_val) for role, hex_val in command.custom_theme_colors.items()},
            )

        settings = AppearanceSettings(
            theme=Theme(command.theme),
            accent_color=Color(command.accent_color),
            interface_density=InterfaceDensity(command.interface_density),
            custom_theme=custom_theme,
        )

        profile.update_appearance(settings)
        await self._profile_repo.update(profile)

        await self._event_bus.publish_all(profile.clear_domain_events())
