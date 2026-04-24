from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.application.ports.oauth.oauth_port import OAuthPort
from app.context.identity.domain.exceptions.user_exceptions import UserNotFoundException
from app.context.identity.domain.repositories.user_auth_repository import UserAuthRepository
from app.context.identity.domain.value_objects.auth_provider import AuthProvider


class LinkOAuthCommand(BaseCommand):
    """
    Команда привязки OAuth-провайдера к аккаунту.

    Атрибуты:
        user_id: Идентификатор пользователя.
        provider: Название провайдера (oauth_google, oauth_github, ...).
        authorization_code: Authorization code от провайдера.
        redirect_uri: URI перенаправления.
    """

    user_id: str
    provider: str
    authorization_code: str
    redirect_uri: str


class LinkOAuthHandler(BaseCommandHandler[LinkOAuthCommand, None]):
    """
    Обработчик привязки OAuth-провайдера.

    Обменивает authorization code на access token через OAuthPort,
    получает профиль пользователя от провайдера, привязывает.
    """

    def __init__(
        self,
        user_auth_repo: UserAuthRepository,
        oauth_port: OAuthPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._user_auth_repo = user_auth_repo
        self._oauth_port = oauth_port
        self._event_bus = event_bus

    async def handle(self, command: LinkOAuthCommand) -> None:
        user_id = Id.from_string(command.user_id)

        user_auth = await self._user_auth_repo.get_by_user_id(user_id)
        if user_auth is None:
            raise UserNotFoundException(command.user_id)

        provider = AuthProvider(command.provider)

        access_token = await self._oauth_port.exchange_code(
            provider=command.provider,
            code=command.authorization_code,
            redirect_uri=command.redirect_uri,
        )
        user_info = await self._oauth_port.get_user_info(
            provider=command.provider,
            access_token=access_token,
        )

        user_auth.link_oauth(
            provider=provider,
            provider_user_id=user_info.provider_user_id,
            email=user_info.email,
            display_name=user_info.display_name,
        )

        await self._user_auth_repo.update(user_auth)
        await self._event_bus.publish_all(user_auth.clear_domain_events())
