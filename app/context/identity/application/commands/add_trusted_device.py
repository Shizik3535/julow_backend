from __future__ import annotations

from datetime import datetime

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.ip_address_vo import IpAddress
from app.context.identity.domain.exceptions.user_exceptions import UserNotFoundException
from app.context.identity.domain.repositories.user_auth_repository import UserAuthRepository
from app.context.identity.domain.value_objects.device_info import DeviceInfo


class AddTrustedDeviceCommand(BaseCommand):
    """
    Команда добавления доверенного устройства.

    Атрибуты:
        user_id: Идентификатор пользователя.
        device_fingerprint: Отпечаток устройства.
        user_agent: User-Agent устройства.
        ip: IP-адрес.
        expires_at: Время истечения доверия (ISO 8601, опционально).
    """

    user_id: str
    device_fingerprint: str
    user_agent: str
    ip: str
    expires_at: datetime | None = None


class AddTrustedDeviceHandler(BaseCommandHandler[AddTrustedDeviceCommand, None]):
    """
    Обработчик добавления доверенного устройства.

    Загружает UserAuth, добавляет устройство, сохраняет.
    """

    def __init__(
        self,
        user_auth_repo: UserAuthRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._user_auth_repo = user_auth_repo
        self._event_bus = event_bus

    async def handle(self, command: AddTrustedDeviceCommand) -> None:
        user_id = Id.from_string(command.user_id)

        user_auth = await self._user_auth_repo.get_by_user_id(user_id)
        if user_auth is None:
            raise UserNotFoundException(command.user_id)

        user_auth.add_trusted_device(
            fingerprint=command.device_fingerprint,
            device_info=DeviceInfo(user_agent=command.user_agent),
            ip=IpAddress(command.ip),
            expires_at=command.expires_at,
        )

        await self._user_auth_repo.update(user_auth)
        await self._event_bus.publish_all(user_auth.clear_domain_events())
