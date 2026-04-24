from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.language_code_vo import LanguageCode
from app.shared.domain.value_objects.timezone_vo import Timezone
from app.context.profile.domain.repositories.user_profile_repository import UserProfileRepository
from app.context.profile.domain.exceptions.profile_exceptions import ProfileNotFoundException
from app.context.profile.domain.value_objects.date_format import DateFormat
from app.context.profile.domain.value_objects.localization_settings import LocalizationSettings
from app.context.profile.domain.value_objects.time_format import TimeFormat
from app.context.profile.domain.value_objects.week_start_day import WeekStartDay


class UpdateLocalizationCommand(BaseCommand):
    """
    Команда обновления настроек локализации.

    Атрибуты:
        user_id: ID пользователя.
        language: Код языка (ISO 639-1, например en, ru).
        timezone: Часовой пояс (IANA, например Europe/Moscow).
        date_format: Паттерн формата даты (например YYYY-MM-DD).
        time_format: Формат времени (H24, H12).
        week_start_day: День начала недели (MONDAY, SUNDAY, SATURDAY).
    """

    user_id: str
    language: str = "en"
    timezone: str = "UTC"
    date_format: str = "YYYY-MM-DD"
    time_format: str = "H24"
    week_start_day: str = "MONDAY"


class UpdateLocalizationHandler(BaseCommandHandler[UpdateLocalizationCommand, None]):
    """
    Обработчик обновления настроек локализации.

    Создаёт VO LocalizationSettings из входных данных,
    вызывает доменный метод update_localization.
    """

    def __init__(self, profile_repo: UserProfileRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._profile_repo = profile_repo
        self._event_bus = event_bus

    async def handle(self, command: UpdateLocalizationCommand) -> None:
        profile = await self._profile_repo.get_by_user_id(Id.from_string(command.user_id))
        if profile is None:
            raise ProfileNotFoundException(command.user_id)

        settings = LocalizationSettings(
            language=LanguageCode(command.language),
            timezone=Timezone(command.timezone),
            date_format=DateFormat(command.date_format),
            time_format=TimeFormat(command.time_format),
            week_start_day=WeekStartDay(command.week_start_day),
        )

        profile.update_localization(settings)
        await self._profile_repo.update(profile)

        await self._event_bus.publish_all(profile.clear_domain_events())
