from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.ip_address_vo import IpAddress
from app.context.identity.domain.value_objects.device_info import DeviceInfo


@dataclass
class TrustedDevice(BaseEntity):
    """
    Сущность доверенного устройства пользователя.

    Принадлежит агрегату UserAuth. Устройство, с которого
    пользователь ранее успешно входил и подтвердил доверие.

    Атрибуты:
        id: Уникальный идентификатор записи.
        device_fingerprint: Уникальный отпечаток устройства.
        device_info: Информация об устройстве.
        ip: IP-адрес, с которого устройство было подтверждено.
        trusted_at: Время добавления в доверенные.
        expires_at: Время истечения доверия (None — бессрочно).
    """

    device_fingerprint: str = ""
    device_info: DeviceInfo = field(default_factory=lambda: DeviceInfo(user_agent="unknown"))
    ip: IpAddress = field(default_factory=lambda: IpAddress("127.0.0.1"))
    trusted_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    expires_at: datetime | None = None

    def is_expired(self) -> bool:
        """Проверяет, истёк ли срок доверия устройства."""
        if self.expires_at is None:
            return False
        return datetime.now(tz=timezone.utc) > self.expires_at
