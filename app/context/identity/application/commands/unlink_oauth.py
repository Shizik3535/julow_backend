from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.domain.exceptions.user_exceptions import UserNotFoundException
from app.context.identity.domain.repositories.user_auth_repository import UserAuthRepository
from app.context.identity.domain.value_objects.auth_provider import AuthProvider


class UnlinkOAuthCommand(BaseCommand):
    """
    Команда отвязки OAuth-провайдера от аккаунта.

    Атрибуты:
        user_id: Идентификатор пользователя.
        provider: Название провайдера (oauth_google, oauth_github, ...).
    """

    user_id: str
    provider: str


class UnlinkOAuthHandler(BaseCommandHandler[UnlinkOAuthCommand, None]):
    """
    Обработчик отвязки OAuth-провайдера.

    Загружает UserAuth, отвязывает провайдер, сохраняет.
    """

    def __init__(
        self,
        user_auth_repo: UserAuthRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._user_auth_repo = user_auth_repo
        self._event_bus = event_bus

    async def handle(self, command: UnlinkOAuthCommand) -> None:
        user_id = Id.from_string(command.user_id)

        user_auth = await self._user_auth_repo.get_by_user_id(user_id)
        if user_auth is None:
            raise UserNotFoundException(command.user_id)

        provider = AuthProvider(command.provider)
        user_auth.unlink_oauth(provider)

        await self._user_auth_repo.update(user_auth)
        await self._event_bus.publish_all(user_auth.clear_domain_events())
