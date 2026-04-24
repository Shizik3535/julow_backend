from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import timezone, timedelta
from zoneinfo import ZoneInfo, available_timezones

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException

_UTC_OFFSET_PATTERN = re.compile(
    r"^UTC([+-])(\d{1,2})(?::(\d{2}))?$", re.IGNORECASE
)

_IANA_ZONES = frozenset(available_timezones())


def _parse_utc_offset(raw: str) -> timezone | None:
    """
    Разбирает строку формата UTC+offset (например UTC+3, UTC-05:30).

    Возвращает timezone или None, если формат не совпадает.
    """
    match = _UTC_OFFSET_PATTERN.match(raw.strip())
    if not match:
        return None
    sign, hours_str, minutes_str = match.groups()
    hours = int(hours_str)
    minutes = int(minutes_str) if minutes_str else 0
    if hours > 14 or minutes > 59 or (hours == 14 and minutes > 0):
        return None
    offset = timedelta(hours=hours, minutes=minutes)
    if sign == "-":
        offset = -offset
    return timezone(offset)


@dataclass(frozen=True)
class Timezone(ValueObject):
    """
    Value Object для часового пояса.

    Поддерживает два формата:
        - Идентификатор IANA (например "Europe/Moscow", "America/New_York")
        - Смещение от UTC (например "UTC+3", "UTC-5", "UTC+05:30")

    Атрибуты:
        value: Идентификатор часового пояса.

    Пример:
        tz1 = Timezone("Europe/Moscow")
        tz2 = Timezone("UTC+3")
        tz3 = Timezone("UTC-05:30")
    """

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        object.__setattr__(self, "value", normalized)

        # Попытка распознать формат UTC±offset
        if _parse_utc_offset(normalized) is not None:
            return

        # Проверка валидности IANA-идентификатора
        if normalized not in _IANA_ZONES:
            raise ValidationException(
                field="timezone",
                message=f"Некорректный часовой пояс: {normalized}",
            )

    @property
    def is_utc_offset(self) -> bool:
        """Является ли значение смещением от UTC."""
        return _parse_utc_offset(self.value) is not None

    @property
    def is_iana(self) -> bool:
        """Является ли значение IANA-идентификатором."""
        return not self.is_utc_offset

    def to_tzinfo(self) -> ZoneInfo | timezone:
        """
        Возвращает объект tzinfo для использования с datetime.

        Возвращает:
            ZoneInfo для IANA-идентификаторов,
            timezone для UTC-смещений.
        """
        if self.is_utc_offset:
            return _parse_utc_offset(self.value)  # type: ignore[return-value]
        return ZoneInfo(self.value)

    def __str__(self) -> str:
        return self.value
