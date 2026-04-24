from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.domain.exceptions.user_exceptions import UserNotFoundException
from app.context.identity.domain.repositories.user_repository import UserRepository


class CancelAccountDeletionCommand(BaseCommand):
    """
    Команда отмены удаления аккаунта.

    Атрибуты:
        user_id: Идентификатор пользователя.
    """

    user_id: str


class CancelAccountDeletionHandler(BaseCommandHandler[CancelAccountDeletionCommand, None]):
    """
    Обработчик отмены удаления аккаунта.

    Загружает User, отменяет удаление, сохраняет.
    Не порождает доменных событий (cancel — тихая операция).
    """

    def __init__(
        self,
        user_repo: UserRepository,
    ) -> None:
        super().__init__()
        self._user_repo = user_repo

    async def handle(self, command: CancelAccountDeletionCommand) -> None:
        user_id = Id.from_string(command.user_id)

        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundException(command.user_id)

        user.cancel_account_deletion()

        await self._user_repo.update(user)
