from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.ip_address_vo import IpAddress
from app.context.identity.domain.events.session_events import (
    AllOtherSessionsTerminated,
    SessionCreated,
    SessionRefreshed,
    SessionTerminated,
)
from app.context.identity.domain.exceptions.session_exceptions import InactiveSessionException
from app.context.identity.domain.value_objects.device_info import DeviceInfo
from app.context.identity.domain.value_objects.geolocation import Geolocation
from app.context.identity.domain.value_objects.refresh_token import RefreshToken
from app.context.identity.domain.value_objects.session_status import SessionStatus


@dataclass
class Session(AggregateRoot):
    """
    Корень агрегата сессии (Identity BC).

    Полностью самостоятельный AR. User и UserAuth не управляют
    сессиями напрямую — только через events.

    Атрибуты:
        user_id: ID пользователя, которому принадлежит сессия.
        device_info: Информация об устройстве.
        ip_address: IP-адрес.
        geolocation: Геолокация (определяется через GeoIP).
        is_remember_me: Флаг «Запомнить меня».
        refresh_token: Refresh-токен.
        status: Статус сессии (ACTIVE, EXPIRED, TERMINATED).
        max_concurrent: Максимальное количество одновременных сессий.
        created_at: Время создания.
        expires_at: Время истечения.
        terminated_at: Время завершения.
    """

    user_id: Id = field(default_factory=Id.generate)
    device_info: DeviceInfo = field(default_factory=lambda: DeviceInfo(user_agent="unknown"))
    ip_address: IpAddress = field(default_factory=lambda: IpAddress("127.0.0.1"))
    geolocation: Geolocation | None = None
    is_remember_me: bool = False
    refresh_token: RefreshToken | None = None
    status: SessionStatus = SessionStatus.ACTIVE
    max_concurrent: int = 5
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    expires_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    terminated_at: datetime | None = None

    # --- Свойства ---

    @property
    def is_active(self) -> bool:
        """Возвращает True, если сессия активна."""
        return self.status == SessionStatus.ACTIVE

    # --- Фабричный метод ---

    @classmethod
    def create(
        cls,
        user_id: Id,
        device_info: DeviceInfo,
        ip_address: IpAddress,
        geolocation: Geolocation | None = None,
        is_remember_me: bool = False,
        refresh_token: RefreshToken | None = None,
        expires_at: datetime | None = None,
        max_concurrent: int = 5,
    ) -> Session:
        """Создаёт новую сессию."""
        if expires_at is None:
            expires_at = datetime.now(tz=timezone.utc) + timedelta(days=30 if is_remember_me else 1)
        session = cls(
            user_id=user_id,
            device_info=device_info,
            ip_address=ip_address,
            geolocation=geolocation,
            is_remember_me=is_remember_me,
            refresh_token=refresh_token,
            status=SessionStatus.ACTIVE,
            max_concurrent=max_concurrent,
            expires_at=expires_at,
        )
        session._register_event(
            SessionCreated(
                user_id=str(user_id),
                ip_address=ip_address.value,
                device_info=device_info.user_agent,
            )
        )
        return session

    # --- Методы ---

    def terminate(self) -> None:
        """Завершает сессию."""
        if self.status == SessionStatus.TERMINATED:
            return
        self.status = SessionStatus.TERMINATED
        self.terminated_at = datetime.now(tz=timezone.utc)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            SessionTerminated(user_id=str(self.user_id), session_id=str(self.id))
        )

    def is_expired(self) -> bool:
        """Проверяет, истёк ли срок действия сессии."""
        if datetime.now(tz=timezone.utc) > self.expires_at:
            if self.status == SessionStatus.ACTIVE:
                self.status = SessionStatus.EXPIRED
            return True
        return False

    def refresh_activity(self) -> None:
        """Обновляет активность сессии (продлевает)."""
        if self.status != SessionStatus.ACTIVE:
            raise InactiveSessionException()
        self.updated_at = datetime.now(tz=timezone.utc)

    def refresh(self, new_refresh_token: RefreshToken, new_expires_at: datetime) -> None:
        """Обновляет refresh-токен и продлевает сессию."""
        if self.status != SessionStatus.ACTIVE:
            raise InactiveSessionException()
        self.refresh_token = new_refresh_token
        self.expires_at = new_expires_at
        self._register_event(SessionRefreshed(user_id=str(self.user_id)))

    @staticmethod
    def create_all_other_sessions_terminated_event(
        user_id: Id, current_session_id: Id
    ) -> AllOtherSessionsTerminated:
        """Создаёт событие завершения всех других сессий. Вызывается из Application layer."""
        return AllOtherSessionsTerminated(
            user_id=str(user_id), current_session_id=str(current_session_id)
        )
