from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject


@dataclass(frozen=True)
class NotificationGroupKey(ValueObject):
    """
    Value Object для ключа группировки уведомлений.

    Одинаковые group_key = одно и то же уведомление (группировка).

    Атрибуты:
        key: Строковый ключ группировки.
    """

    key: str = ""

    def __str__(self) -> str:
        return self.key
