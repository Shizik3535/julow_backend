from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject


@dataclass(frozen=True)
class SessionPolicyConfig(ValueObject):
    """Настройки политики сессий."""

    max_duration_minutes: int | None = None
    idle_timeout_minutes: int | None = None
    enforce_single_session: bool = False
