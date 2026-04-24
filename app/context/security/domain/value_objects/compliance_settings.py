from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_value_object import ValueObject
from app.context.security.domain.value_objects.data_residency import DataResidency


@dataclass(frozen=True)
class ComplianceSettings(ValueObject):
    """Настройки compliance стандарта."""

    data_residency: DataResidency | None = None
    require_encryption_at_rest: bool = True
    require_encryption_in_transit: bool = True
    require_mfa: bool = False
    audit_log_retention_days: int = 365
    data_retention_days: int | None = None
    allowed_ip_ranges: list[str] | None = None
