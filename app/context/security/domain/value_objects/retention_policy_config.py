from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject


@dataclass(frozen=True)
class RetentionPolicyConfig(ValueObject):
    """Настройки политики хранения данных."""

    audit_log_days: int = 365
    security_events_days: int = 365
    backup_retention_days: int = 90
