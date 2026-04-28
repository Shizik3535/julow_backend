from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.events.notification_events import (
    DeviceTokenRegistered,
    DeviceTokenRemoved,
)


@dataclass
class DeviceToken(AggregateRoot):
    """
    Корень агрегата токена устройства (Notification BC).

    Хранит идентификатор устройства для push-уведомлений.
    Один пользователь может иметь несколько устройств.

    Атрибуты:
        user_id: ID пользователя-владельца.
        token: Push-токен устройства (FCM/APNs).
        platform: Платформа устройства (ios/android/web).
        device_name: Название устройства.
        is_active: Активен ли токен.
        last_used_at: Время последнего использования.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    user_id: Id = field(default_factory=Id.generate)
    token: str = ""
    platform: str = ""
    device_name: str = ""
    is_active: bool = True
    last_used_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create(
        cls,
        user_id: Id,
        token: str,
        platform: str,
        device_name: str = "",
    ) -> DeviceToken:
        """Регистрирует токен устройства."""
        device_token = cls(
            user_id=user_id,
            token=token,
            platform=platform,
            device_name=device_name,
        )
        device_token._register_event(
            DeviceTokenRegistered(
                user_id=str(user_id),
                platform=platform,
            )
        )
        return device_token

    def deactivate(self) -> None:
        """Деактивирует токен устройства."""
        if not self.is_active:
            return
        self.is_active = False
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            DeviceTokenRemoved(
                user_id=str(self.user_id),
                platform=self.platform,
            )
        )

    def mark_used(self) -> None:
        """Обновляет время последнего использования."""
        self.last_used_at = datetime.now(tz=timezone.utc)
        self.updated_at = datetime.now(tz=timezone.utc)

    def update_token(self, new_token: str) -> None:
        """Обновляет push-токен (при обновлении на устройстве)."""
        self.token = new_token
        self.updated_at = datetime.now(tz=timezone.utc)
