from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.ip_address_vo import IpAddress
from app.context.identity.application.dto.session_dto import SessionDTO
from app.context.identity.domain.aggregates.session import Session
from app.context.identity.domain.repositories.session_repository import SessionRepository
from app.context.identity.domain.value_objects.device_info import DeviceInfo


class CreateSessionCommand(BaseCommand):
    """
    Команда создания сессии.

    Используется когда сессия создаётся отдельно от логина
    (например, при OAuth-аутентификации).

    Атрибуты:
        user_id: Идентификатор пользователя.
        ip: IP-адрес клиента.
        user_agent: User-Agent клиента.
        is_remember_me: Флаг «Запомнить меня».
    """

    user_id: str
    ip: str = "127.0.0.1"
    user_agent: str = "unknown"
    is_remember_me: bool = False


class CreateSessionHandler(BaseCommandHandler[CreateSessionCommand, SessionDTO]):
    """
    Обработчик создания сессии.

    Создаёт новую сессию для пользователя.
    """

    def __init__(
        self,
        session_repo: SessionRepository,
    ) -> None:
        super().__init__()
        self._session_repo = session_repo

    async def handle(self, command: CreateSessionCommand) -> SessionDTO:
        session = Session.create(
            user_id=Id.from_string(command.user_id),
            device_info=DeviceInfo(user_agent=command.user_agent),
            ip_address=IpAddress(command.ip),
            is_remember_me=command.is_remember_me,
        )

        await self._session_repo.add(session)

        return SessionDTO(
            id=str(session.id),
            user_id=str(session.user_id),
            device_info=session.device_info.user_agent,
            ip_address=session.ip_address.value,
            status=session.status.value,
            is_remember_me=session.is_remember_me,
            created_at=session.created_at,
            expires_at=session.expires_at,
        )
