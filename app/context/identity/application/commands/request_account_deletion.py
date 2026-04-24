from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.domain.exceptions.user_exceptions import UserNotFoundException
from app.context.identity.domain.repositories.user_repository import UserRepository


class RequestAccountDeletionCommand(BaseCommand):
    """
    Команда запроса удаления аккаунта.

    Атрибуты:
        user_id: Идентификатор пользователя.
    """

    user_id: str


class RequestAccountDeletionHandler(BaseCommandHandler[RequestAccountDeletionCommand, None]):
    """
    Обработчик запроса удаления аккаунта.

    Загружает User, переводит в статус PENDING_DELETION, сохраняет.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._user_repo = user_repo
        self._event_bus = event_bus

    async def handle(self, command: RequestAccountDeletionCommand) -> None:
        user_id = Id.from_string(command.user_id)

        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundException(command.user_id)

        user.request_account_deletion()

        await self._user_repo.update(user)
        await self._event_bus.publish_all(user.clear_domain_events())
