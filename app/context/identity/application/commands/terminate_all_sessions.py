from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.domain.repositories.session_repository import SessionRepository


class TerminateAllSessionsCommand(BaseCommand):
    """
    Команда завершения всех сессий пользователя, кроме текущей.

    Атрибуты:
        user_id: Идентификатор пользователя.
        current_session_id: ID текущей сессии (не завершать).
    """

    user_id: str
    current_session_id: str


class TerminateAllSessionsHandler(BaseCommandHandler[TerminateAllSessionsCommand, int]):
    """
    Обработчик завершения всех сессий кроме текущей.

    Возвращает количество завершённых сессий.
    """

    def __init__(
        self,
        session_repo: SessionRepository,
    ) -> None:
        super().__init__()
        self._session_repo = session_repo

    async def handle(self, command: TerminateAllSessionsCommand) -> int:
        user_id = Id.from_string(command.user_id)
        current_session_id = Id.from_string(command.current_session_id)

        terminated_count = await self._session_repo.terminate_all_by_user(
            user_id=user_id,
            except_session_id=current_session_id,
        )

        return terminated_count
