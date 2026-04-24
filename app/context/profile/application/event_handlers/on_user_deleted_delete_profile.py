from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.profile.domain.repositories.user_profile_repository import UserProfileRepository


class OnUserDeletedDeleteProfile(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события UserDeleted из Identity BC.

    Подписывается на топик «identity.events» и реагирует
    на событие «UserDeleted»: помечает профиль как удалённый.

    Если профиль не найден — логирует предупреждение
    и пропускает (идемпотентность).
    """

    def __init__(self, profile_repo: UserProfileRepository) -> None:
        super().__init__()
        self._profile_repo = profile_repo

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "UserDeleted":
            return

        payload = event.get("payload", {})
        user_id_str = payload.get("user_id")
        if not user_id_str:
            self._logger.warning(
                "UserDeleted event missing user_id",
                event_data=event,
            )
            return

        user_id = Id.from_string(user_id_str)

        profile = await self._profile_repo.get_by_user_id(user_id)
        if profile is None:
            self._logger.warning(
                "Profile not found for deleted user, skipping",
                user_id=user_id_str,
            )
            return

        profile.delete()
        await self._profile_repo.update(profile)

        self._logger.info(
            "Profile marked as deleted for user",
            user_id=user_id_str,
            profile_id=str(profile.id),
        )
