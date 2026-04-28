from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.repositories.device_token_repository import DeviceTokenRepository
from app.context.notification.application.dto.device_token_dto import DeviceTokenDTO
from app.context.notification.application.dto.device_token_list_dto import DeviceTokenListDTO


class GetDeviceTokensQuery(BaseQuery):
    """
    Запрос списка токенов устройств.

    Атрибуты:
        user_id: ID пользователя.
        active_only: Только активные токены.
    """

    user_id: str
    active_only: bool = False


class GetDeviceTokensHandler(BaseQueryHandler[GetDeviceTokensQuery, DeviceTokenListDTO]):
    """Обработчик запроса списка токенов устройств."""

    def __init__(self, device_token_repo: DeviceTokenRepository) -> None:
        super().__init__()
        self._repo = device_token_repo

    async def handle(self, query: GetDeviceTokensQuery) -> DeviceTokenListDTO:
        user_id = Id.from_string(query.user_id)

        if query.active_only:
            tokens = await self._repo.get_active_by_user_id(user_id)
        else:
            tokens = await self._repo.get_by_user_id(user_id)

        items = [
            DeviceTokenDTO(
                id=str(t.id),
                platform=t.platform,
                device_name=t.device_name,
                is_active=t.is_active,
                last_used_at=t.last_used_at,
            )
            for t in tokens
        ]

        return DeviceTokenListDTO(items=items)
