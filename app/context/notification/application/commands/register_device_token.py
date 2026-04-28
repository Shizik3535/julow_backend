from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.aggregates.device_token import DeviceToken
from app.context.notification.domain.repositories.device_token_repository import DeviceTokenRepository
from app.context.notification.application.exceptions.notification_app_exceptions import DeviceTokenAlreadyExistsException
from app.context.notification.application.dto.device_token_dto import DeviceTokenDTO


class RegisterDeviceTokenCommand(BaseCommand):
    """
    Команда регистрации токена устройства.

    Атрибуты:
        user_id: ID пользователя.
        token: Push-токен устройства.
        platform: Платформа (ios/android/web).
        device_name: Название устройства.
    """

    user_id: str
    token: str
    platform: str
    device_name: str = ""


class RegisterDeviceTokenHandler(BaseCommandHandler[RegisterDeviceTokenCommand, DeviceTokenDTO]):
    """Обработчик регистрации токена устройства."""

    def __init__(
        self,
        device_token_repo: DeviceTokenRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = device_token_repo
        self._event_bus = event_bus

    async def handle(self, command: RegisterDeviceTokenCommand) -> DeviceTokenDTO:
        # Проверяем, не зарегистрирован ли уже этот токен
        existing = await self._repo.get_by_token(command.token)
        if existing is not None:
            raise DeviceTokenAlreadyExistsException(command.token)

        user_id = Id.from_string(command.user_id)
        device_token = DeviceToken.create(
            user_id=user_id,
            token=command.token,
            platform=command.platform,
            device_name=command.device_name,
        )

        try:
            await self._repo.add(device_token)
        except Exception as exc:
            # Race condition: конкурентный запрос уже вставил токен (unique constraint)
            if "unique" in str(exc).lower() or "duplicate" in str(exc).lower() or "UniqueViolation" in type(exc).__name__:
                raise DeviceTokenAlreadyExistsException(command.token)
            raise

        await self._event_bus.publish_all(device_token.clear_domain_events())

        return DeviceTokenDTO(
            id=str(device_token.id),
            platform=device_token.platform,
            device_name=device_token.device_name,
            is_active=device_token.is_active,
            last_used_at=device_token.last_used_at,
        )
