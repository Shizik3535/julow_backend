from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id
from app.context.security.domain.value_objects.security_event_type import SecurityEventType
from app.context.security.domain.value_objects.incident_severity import IncidentSeverity


@dataclass
class SecurityEvent(BaseEntity):
    event_type: SecurityEventType = SecurityEventType.OTHER
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    details: dict[str, str] = field(default_factory=dict)
    is_resolved: bool = False
    resolved_at: datetime | None = None
    resolved_by: Id | None = None
