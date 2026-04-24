from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class PasswordPolicy(ValueObject):
    """
    Value Object для политики паролей.

    Определяет требования к сложности пароля и срок его действия.

    Атрибуты:
        min_length: Минимальная длина пароля.
        require_upper: Требуется хотя бы одна заглавная буква.
        require_lower: Требуется хотя бы одна строчная буква.
        require_digit: Требуется хотя бы одна цифра.
        require_special: Требуется хотя бы один спецсимвол.
        max_age_days: Максимальный срок действия пароля в днях (None — без ограничения).
    """

    min_length: int = 8
    require_upper: bool = True
    require_lower: bool = True
    require_digit: bool = True
    require_special: bool = False
    max_age_days: int | None = None

    def __post_init__(self) -> None:
        if self.min_length < 1:
            raise ValidationException(
                field="min_length",
                message="Минимальная длина пароля должна быть >= 1",
            )
        if self.max_age_days is not None and self.max_age_days < 1:
            raise ValidationException(
                field="max_age_days",
                message="Максимальный срок действия пароля должен быть >= 1 дня",
            )
