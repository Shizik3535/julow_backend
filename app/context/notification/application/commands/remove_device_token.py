from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.repositories.device_token_repository import DeviceTokenRepository
from app.context.notification.domain.exceptions.notification_exceptions import DeviceTokenNotFoundException


class RemoveDeviceTokenCommand(BaseCommand):
    """
    Команда удаления/деактивации токена устройства.

    Атрибуты:
        device_token_id: ID агрегата DeviceToken.
    """

    device_token_id: str


class RemoveDeviceTokenHandler(BaseCommandHandler[RemoveDeviceTokenCommand, None]):
    """Обработчик удаления/деактивации токена устройства."""

    def __init__(
        self,
        device_token_repo: DeviceTokenRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = device_token_repo
        self._event_bus = event_bus

    async def handle(self, command: RemoveDeviceTokenCommand) -> None:
        device_token = await self._repo.get_by_id(Id.from_string(command.device_token_id))
        if device_token is None:
            raise DeviceTokenNotFoundException(command.device_token_id)

        device_token.deactivate()
        await self._repo.update(device_token)
        await self._event_bus.publish_all(device_token.clear_domain_events())
