from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class RefreshToken(ValueObject):
    """
    Value Object для refresh-токена сессии.

    Атрибуты:
        value: Строка refresh-токена.
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValidationException(
                field="refresh_token",
                message="Refresh-токен не может быть пустым",
            )

    def __str__(self) -> str:
        return self.value
