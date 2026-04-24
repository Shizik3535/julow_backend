from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.domain.repositories.user_auth_repository import UserAuthRepository
from app.context.identity.domain.repositories.user_repository import UserRepository


class ConfirmEmailCommand(BaseCommand):
    """
    Команда подтверждения email по токену.

    Атрибуты:
        user_id: Идентификатор пользователя.
        token: Токен верификации.
    """

    user_id: str
    token: str


class ConfirmEmailHandler(BaseCommandHandler[ConfirmEmailCommand, None]):
    """
    Обработчик подтверждения email.

    Верифицирует токен в UserAuth и подтверждает email в User.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        user_auth_repo: UserAuthRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._user_repo = user_repo
        self._user_auth_repo = user_auth_repo
        self._event_bus = event_bus

    async def handle(self, command: ConfirmEmailCommand) -> None:
        user_id = Id.from_string(command.user_id)

        user_auth = await self._user_auth_repo.get_by_user_id(user_id)
        if user_auth is None:
            from app.context.identity.domain.exceptions.user_exceptions import UserNotFoundException
            raise UserNotFoundException(command.user_id)

        user_auth.verify_email(command.token)
        await self._user_auth_repo.update(user_auth)

        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            from app.context.identity.domain.exceptions.user_exceptions import UserNotFoundException
            raise UserNotFoundException(command.user_id)

        user.confirm_email()
        await self._user_repo.update(user)

        await self._event_bus.publish_all(user_auth.clear_domain_events())
        await self._event_bus.publish_all(user.clear_domain_events())
