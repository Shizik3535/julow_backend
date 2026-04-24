from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.application.dto.trusted_device_dto import TrustedDeviceDTO
from app.context.identity.application.dto.trusted_device_list_dto import TrustedDeviceListDTO
from app.context.identity.domain.exceptions.user_exceptions import UserNotFoundException
from app.context.identity.domain.repositories.user_auth_repository import UserAuthRepository


class GetTrustedDevicesQuery(BaseQuery):
    """
    Запрос списка доверенных устройств пользователя.

    Атрибуты:
        user_id: Идентификатор пользователя.
    """

    user_id: str


class GetTrustedDevicesHandler(BaseQueryHandler[GetTrustedDevicesQuery, TrustedDeviceListDTO]):
    """
    Обработчик запроса доверенных устройств.
    """

    def __init__(self, user_auth_repo: UserAuthRepository) -> None:
        super().__init__()
        self._user_auth_repo = user_auth_repo

    async def handle(self, query: GetTrustedDevicesQuery) -> TrustedDeviceListDTO:
        user_id = Id.from_string(query.user_id)

        user_auth = await self._user_auth_repo.get_by_user_id(user_id)
        if user_auth is None:
            raise UserNotFoundException(query.user_id)

        items = [
            TrustedDeviceDTO(
                device_fingerprint=d.device_fingerprint,
                user_agent=d.device_info.user_agent,
                ip=d.ip.value,
                trusted_at=d.trusted_at,
                expires_at=d.expires_at,
            )
            for d in user_auth.trusted_devices
            if not d.is_expired()
        ]

        return TrustedDeviceListDTO(items=items, total=len(items))
