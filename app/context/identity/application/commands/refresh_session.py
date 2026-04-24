from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.ports.auth.auth_port import AuthTokenPort
from app.context.identity.application.dto.auth_result_dto import AuthResultDTO
from app.context.identity.application.dto.user_dto import UserDTO
from app.context.identity.application.exceptions.session_app_exceptions import InvalidRefreshTokenException
from app.context.identity.domain.exceptions.user_exceptions import UserNotFoundException
from app.context.identity.domain.repositories.session_repository import SessionRepository
from app.context.identity.domain.repositories.user_repository import UserRepository
from app.context.identity.domain.value_objects.refresh_token import RefreshToken


class RefreshSessionCommand(BaseCommand):
    """
    Команда обновления сессии по refresh-токену.

    Атрибуты:
        refresh_token: Текущий refresh-токен.
    """

    refresh_token: str


class RefreshSessionHandler(BaseCommandHandler[RefreshSessionCommand, AuthResultDTO]):
    """
    Обработчик обновления сессии.

    Находит сессию по refresh-токену, генерирует новую пару токенов,
    обновляет сессию.
    """

    REFRESH_TTL_DAYS: int = 30

    def __init__(
        self,
        session_repo: SessionRepository,
        user_repo: UserRepository,
        auth_token_port: AuthTokenPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._session_repo = session_repo
        self._user_repo = user_repo
        self._auth_token_port = auth_token_port
        self._event_bus = event_bus

    async def handle(self, command: RefreshSessionCommand) -> AuthResultDTO:
        old_token = RefreshToken(value=command.refresh_token)

        session = await self._session_repo.get_by_refresh_token(old_token)
        if session is None or not session.is_active:
            raise InvalidRefreshTokenException()

        if session.is_expired():
            raise InvalidRefreshTokenException()

        user = await self._user_repo.get_by_id(session.user_id)
        if user is None:
            raise UserNotFoundException(str(session.user_id))

        token_pair = self._auth_token_port.generate_token_pair(str(user.id))
        new_expires_at = datetime.now(tz=timezone.utc) + timedelta(days=self.REFRESH_TTL_DAYS)

        session.refresh(
            new_refresh_token=RefreshToken(value=token_pair.refresh_token),
            new_expires_at=new_expires_at,
        )

        await self._session_repo.update(session)
        await self._event_bus.publish_all(session.clear_domain_events())

        return AuthResultDTO(
            user=UserDTO(
                id=str(user.id),
                email=user.email.value,
                status=user.status.value,
                role_ids=[str(rid) for rid in user.role_ids],
                is_email_confirmed=user.is_email_confirmed,
                created_at=user.created_at,
                updated_at=user.updated_at,
            ),
            access_token=token_pair.access_token,
            refresh_token=token_pair.refresh_token,
            access_expires_in=token_pair.access_expires_in,
            refresh_expires_in=token_pair.refresh_expires_in,
        )
