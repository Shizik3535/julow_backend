from __future__ import annotations

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import EntityNotFoundException


class SessionNotFoundException(EntityNotFoundException):
    """Сессия не найдена."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="Session", id=id)


class SessionExpiredException(DomainException):
    """Сессия истекла."""

    def __init__(self) -> None:
        super().__init__("Сессия истекла")


class InactiveSessionException(DomainException):
    """Нельзя обновить неактивную сессию."""

    def __init__(self) -> None:
        super().__init__("Нельзя обновить неактивную сессию")


class UnauthorizedSessionAccessException(DomainException):
    """Попытка доступа к чужой сессии."""

    def __init__(self) -> None:
        super().__init__("Нет доступа к данной сессии")
