from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_entity import BaseEntity
from app.context.security.domain.value_objects.compliance_standard import ComplianceStandard
from app.context.security.domain.value_objects.compliance_settings import ComplianceSettings


@dataclass
class ComplianceConfig(BaseEntity):
    standard: ComplianceStandard = ComplianceStandard.GDPR
    is_enabled: bool = True
    settings: ComplianceSettings = field(default_factory=ComplianceSettings)
