from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_domain_event import BaseDomainEvent
from app.context.security.domain.value_objects.compliance_standard import ComplianceStandard
from app.context.security.domain.value_objects.data_subject_request_type import DataSubjectRequestType


@dataclass(frozen=True)
class SecurityPolicyUpdated(BaseDomainEvent):
    policy_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ComplianceViolationDetected(BaseDomainEvent):
    standard: ComplianceStandard = ComplianceStandard.GDPR
    violation_details: str = ""


@dataclass(frozen=True)
class DataSubjectRequestCreated(BaseDomainEvent):
    request_id: str = ""
    user_id: str = ""
    request_type: DataSubjectRequestType = DataSubjectRequestType.EXPORT


@dataclass(frozen=True)
class DataSubjectRequestCompleted(BaseDomainEvent):
    request_id: str = ""


@dataclass(frozen=True)
class DataSubjectRequestRejected(BaseDomainEvent):
    request_id: str = ""
    reason: str = ""
