from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class PasswordHash(ValueObject):
    """
    Value Object для хеша пароля.

    Хранит результат хеширования пароля (bcrypt / argon2).
    Само хеширование выполняется на уровне инфраструктуры.

    Атрибуты:
        value: Строка хеша пароля.
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValidationException(
                field="password_hash",
                message="PasswordHash не может быть пустым",
            )

    def __str__(self) -> str:
        return self.value
