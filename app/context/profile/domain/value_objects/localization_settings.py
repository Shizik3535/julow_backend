from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.value_objects.language_code_vo import LanguageCode
from app.shared.domain.value_objects.timezone_vo import Timezone
from app.context.profile.domain.value_objects.date_format import DateFormat
from app.context.profile.domain.value_objects.time_format import TimeFormat
from app.context.profile.domain.value_objects.week_start_day import WeekStartDay


@dataclass(frozen=True)
class LocalizationSettings(ValueObject):
    """
    Группа настроек локализации.

    Атрибуты:
        language: Код языка (ISO 639-1).
        timezone: Часовой пояс.
        date_format: Паттерн формата даты.
        time_format: Формат времени (12/24 ч).
        week_start_day: День начала недели.
    """

    language: LanguageCode = field(default_factory=lambda: LanguageCode("en"))
    timezone: Timezone = field(default_factory=lambda: Timezone("UTC"))
    date_format: DateFormat = field(default_factory=lambda: DateFormat("YYYY-MM-DD"))
    time_format: TimeFormat = TimeFormat.H24
    week_start_day: WeekStartDay = WeekStartDay.MONDAY
