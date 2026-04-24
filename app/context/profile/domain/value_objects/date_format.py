from __future__ import annotations

import re
from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException

_DATE_FORMAT_PATTERN = re.compile(r"^[DMY]{2,4}[./\-][DMY]{2,4}[./\-][DMY]{2,4}$")

PRESET_DATE_FORMATS = {
    "ISO": "YYYY-MM-DD",
    "EU_DOTS": "DD.MM.YYYY",
    "US_SLASHES": "MM/DD/YYYY",
    "EU_SLASHES": "DD/MM/YYYY",
    "ASIAN_SLASHES": "YYYY/MM/DD",
}


@dataclass(frozen=True)
class DateFormat(ValueObject):
    """
    Формат даты (validated string).

    Форматов дат может быть сколь угодно много (локали).
    Валидация через паттерн, а не enum.
    Предустановленные паттерны доступны как константы на app-слое.

    Атрибуты:
        value: Паттерн формата даты (например "DD.MM.YYYY", "YYYY-MM-DD").
    """

    value: str

    def __post_init__(self) -> None:
        if not _DATE_FORMAT_PATTERN.match(self.value):
            raise ValidationException(
                field="date_format",
                message=f"Некорректный паттерн формата даты: {self.value}",
            )
        letters = self.value.replace(".", "").replace("/", "").replace("-", "")
        if letters.count("D") != 2 or letters.count("M") != 2 or letters.count("Y") != 4:
            raise ValidationException(
                field="date_format",
                message=f"Паттерн даты должен содержать ровно 2 D, 2 M, 4 Y: {self.value}",
            )

    def __str__(self) -> str:
        return self.value
