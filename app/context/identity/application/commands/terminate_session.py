from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.domain.exceptions.session_exceptions import SessionNotFoundException
from app.context.identity.domain.repositories.session_repository import SessionRepository


class TerminateSessionCommand(BaseCommand):
    """
    Команда завершения одной сессии.

    Атрибуты:
        user_id: Идентификатор пользователя (для проверки владения).
        session_id: Идентификатор сессии для завершения.
    """

    user_id: str
    session_id: str


class TerminateSessionHandler(BaseCommandHandler[TerminateSessionCommand, None]):
    """
    Обработчик завершения одной сессии.

    Находит сессию, проверяет принадлежность пользователю и завершает.
    """

    def __init__(
        self,
        session_repo: SessionRepository,
    ) -> None:
        super().__init__()
        self._session_repo = session_repo

    async def handle(self, command: TerminateSessionCommand) -> None:
        session_id = Id.from_string(command.session_id)

        session = await self._session_repo.get_by_id(session_id)
        if session is None:
            raise SessionNotFoundException(command.session_id)

        if str(session.user_id) != command.user_id:
            from app.context.identity.domain.exceptions.session_exceptions import (
                UnauthorizedSessionAccessException,
            )
            raise UnauthorizedSessionAccessException()

        session.terminate()
        await self._session_repo.update(session)
