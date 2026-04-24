from __future__ import annotations

import re
from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException

_EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


@dataclass(frozen=True)
class Email(ValueObject):
    """
    Value Object для email-адреса.

    Гарантирует, что значение является валидным email-адресом.
    Хранится в нижнем регистре для единообразия.

    Атрибуты:
        value: Нормализованный email-адрес.

    Пример:
        email = Email("User@Example.COM")
        print(email.value)  # "user@example.com"
    """

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        object.__setattr__(self, "value", normalized)
        if not _EMAIL_PATTERN.match(normalized):
            raise ValidationException(
                field="email",
                message=f"Некорректный формат email: {normalized}",
            )

    def __str__(self) -> str:
        return self.value
