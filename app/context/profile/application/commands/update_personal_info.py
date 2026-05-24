from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.profile.domain.repositories.user_profile_repository import UserProfileRepository
from app.context.profile.domain.exceptions.profile_exceptions import ProfileNotFoundException


class UpdatePersonalInfoCommand(BaseCommand):
    """
    Команда обновления персональных данных профиля.

    Атрибуты:
        user_id: ID пользователя.
        bio: Новый текст «О себе» (None — не менять).
        job_title: Новая должность (None — не менять).
    """

    user_id: str
    display_name: str | None = None
    bio: str | None = None
    job_title: str | None = None


class UpdatePersonalInfoHandler(BaseCommandHandler[UpdatePersonalInfoCommand, None]):
    """
    Обработчик обновления персональных данных.

    Загружает профиль по user_id, обновляет переданные поля,
    сохраняет изменения.
    """

    def __init__(self, profile_repo: UserProfileRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._profile_repo = profile_repo
        self._event_bus = event_bus

    async def handle(self, command: UpdatePersonalInfoCommand) -> None:
        profile = await self._profile_repo.get_by_user_id(Id.from_string(command.user_id))
        if profile is None:
            raise ProfileNotFoundException(command.user_id)

        profile.update_personal_info(
            display_name=command.display_name,
            bio=command.bio,
            job_title=command.job_title,
        )

        await self._profile_repo.update(profile)

        await self._event_bus.publish_all(profile.clear_domain_events())
