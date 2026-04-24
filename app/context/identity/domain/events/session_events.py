from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_domain_event import BaseDomainEvent


@dataclass(frozen=True)
class SessionCreated(BaseDomainEvent):
    """Сессия создана."""

    user_id: str = ""
    ip_address: str = ""
    device_info: str = ""


@dataclass(frozen=True)
class SessionTerminated(BaseDomainEvent):
    """Сессия завершена."""

    user_id: str = ""
    session_id: str = ""


@dataclass(frozen=True)
class AllOtherSessionsTerminated(BaseDomainEvent):
    """Все другие сессии завершены, кроме текущей."""

    user_id: str = ""
    current_session_id: str = ""


@dataclass(frozen=True)
class SessionRefreshed(BaseDomainEvent):
    """Сессия обновлена (refresh token)."""

    user_id: str = ""
