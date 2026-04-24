from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_domain_event import BaseDomainEvent
from app.context.security.domain.value_objects.security_event_type import SecurityEventType
from app.context.security.domain.value_objects.incident_severity import IncidentSeverity


@dataclass(frozen=True)
class SuspiciousActivityDetected(BaseDomainEvent):
    actor_id: str = ""
    event_type: SecurityEventType = SecurityEventType.OTHER
    reason: str = ""


@dataclass(frozen=True)
class SecurityEventOccurred(BaseDomainEvent):
    event_type: SecurityEventType = SecurityEventType.OTHER
    severity: IncidentSeverity = IncidentSeverity.MEDIUM


@dataclass(frozen=True)
class SecurityEventResolved(BaseDomainEvent):
    event_id: str = ""
    resolved_by: str = ""


@dataclass(frozen=True)
class SecurityIncidentCreated(BaseDomainEvent):
    incident_id: str = ""
    severity: IncidentSeverity = IncidentSeverity.MEDIUM


@dataclass(frozen=True)
class SecurityIncidentUpdated(BaseDomainEvent):
    incident_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SecurityIncidentResolved(BaseDomainEvent):
    incident_id: str = ""
    resolved_by: str = ""
    resolution: str = ""
