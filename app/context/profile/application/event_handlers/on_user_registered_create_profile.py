from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.profile.application.exceptions.profile_app_exceptions import (
    ProfileAlreadyExistsException,
)
from app.context.profile.domain.aggregates.user_profile import UserProfile
from app.context.profile.domain.repositories.user_profile_repository import UserProfileRepository


class OnUserRegisteredCreateProfile(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события UserRegistered из Identity BC.

    Подписывается на топик «identity.events» и реагирует
    на событие «UserRegistered»: создаёт профиль пользователя
    с настройками по умолчанию.

    Если профиль уже существует — логирует предупреждение
    и пропускает (идемпотентность).
    """

    def __init__(self, profile_repo: UserProfileRepository) -> None:
        super().__init__()
        self._profile_repo = profile_repo

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "UserRegistered":
            return

        payload = event.get("payload", {})
        user_id_str = payload.get("user_id")
        if not user_id_str:
            self._logger.warning(
                "UserRegistered event missing user_id",
                event_data=event,
            )
            return

        user_id = Id.from_string(user_id_str)

        existing = await self._profile_repo.get_by_user_id(user_id)
        if existing is not None:
            self._logger.warning(
                "Profile already exists for user, skipping",
                user_id=user_id_str,
            )
            return

        profile = UserProfile.create(user_id=user_id)
        await self._profile_repo.add(profile)

        self._logger.info(
            "Profile created for new user",
            user_id=user_id_str,
            profile_id=str(profile.id),
        )
