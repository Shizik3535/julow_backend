from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class DeviceInfo(ValueObject):
    """
    Value Object для информации об устройстве.

    Атрибуты:
        user_agent: Полный User-Agent заголовок.
        os: Операционная система (распарсенная).
        browser: Браузер (распарсенный).
        device_type: Тип устройства (desktop / mobile / tablet).
    """

    user_agent: str
    os: str | None = None
    browser: str | None = None
    device_type: str | None = None

    def __post_init__(self) -> None:
        if not self.user_agent or not self.user_agent.strip():
            raise ValidationException(
                field="user_agent",
                message="User-Agent не может быть пустым",
            )
