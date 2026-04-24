from __future__ import annotations

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.ip_address_vo import IpAddress
from app.context.identity.domain.aggregates.session import Session
from app.context.identity.domain.events.auth_events import UserLoggedIn
from app.context.identity.domain.repositories.session_repository import SessionRepository
from app.context.identity.domain.value_objects.device_info import DeviceInfo


class OnUserLoggedInCreateSession(BaseEventHandler[UserLoggedIn]):
    """
    Обработчик события UserLoggedIn.

    Создаёт новую сессию при успешном входе пользователя.
    Реализует межагрегатное взаимодействие внутри Identity BC:
    UserAuth → (event) → Session.

    Используется когда создание сессии управляется через события,
    а не напрямую в LoginUserHandler.
    """

    def __init__(self, session_repo: SessionRepository) -> None:
        super().__init__()
        self._session_repo = session_repo

    async def handle(self, event: UserLoggedIn) -> None:
        session = Session.create(
            user_id=Id.from_string(event.user_id),
            device_info=DeviceInfo(user_agent=event.device),
            ip_address=IpAddress(event.ip),
        )

        await self._session_repo.add(session)

        self._logger.info(
            "Session created from UserLoggedIn event",
            user_id=event.user_id,
            session_id=str(session.id),
        )
