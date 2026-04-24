from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject


@dataclass(frozen=True)
class PasswordPolicyConfig(ValueObject):
    """Настройки политики паролей."""

    min_length: int = 8
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digit: bool = True
    require_special: bool = False
    max_age_days: int | None = None
    history_count: int | None = None
