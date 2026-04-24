from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.domain.exceptions.user_exceptions import UserNotFoundException
from app.context.identity.domain.repositories.user_auth_repository import UserAuthRepository
from app.context.identity.domain.value_objects.two_factor_method import TwoFactorMethod


class DisableAuthFactorCommand(BaseCommand):
    """
    Команда отключения фактора 2FA.

    Атрибуты:
        user_id: Идентификатор пользователя.
        method: Метод 2FA (totp, email_code, app).
    """

    user_id: str
    method: str


class DisableAuthFactorHandler(BaseCommandHandler[DisableAuthFactorCommand, None]):
    """
    Обработчик отключения фактора 2FA.

    Загружает UserAuth, отключает фактор, сохраняет.
    """

    def __init__(
        self,
        user_auth_repo: UserAuthRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._user_auth_repo = user_auth_repo
        self._event_bus = event_bus

    async def handle(self, command: DisableAuthFactorCommand) -> None:
        user_id = Id.from_string(command.user_id)

        user_auth = await self._user_auth_repo.get_by_user_id(user_id)
        if user_auth is None:
            raise UserNotFoundException(command.user_id)

        method = TwoFactorMethod(command.method)
        user_auth.disable_auth_factor(method)

        await self._user_auth_repo.update(user_auth)
        await self._event_bus.publish_all(user_auth.clear_domain_events())
