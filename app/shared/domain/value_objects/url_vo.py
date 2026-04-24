from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class Url(ValueObject):
    """
    Value Object для URL.

    Гарантирует, что значение является валидным URL с обязательной схемой.

    Атрибуты:
        value: Строковое представление URL.

    Пример:
        url = Url("https://example.com/path")
    """

    value: str

    def __post_init__(self) -> None:
        parsed = urlparse(self.value)
        if not parsed.scheme or not parsed.netloc:
            raise ValidationException(
                field="url",
                message=f"Некорректный формат URL: {self.value}",
            )

    def __str__(self) -> str:
        return self.value
