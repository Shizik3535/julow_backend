from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.context.security.domain.value_objects.security_event_type import SecurityEventType
from app.context.security.domain.value_objects.incident_severity import IncidentSeverity
from app.context.security.domain.value_objects.incident_status import IncidentStatus
from app.context.security.domain.value_objects.audit_resource import AuditResource
from app.context.security.domain.entities.security_event import SecurityEvent
from app.context.security.domain.entities.incident_note import IncidentNote
from app.context.security.domain.events.security_events import (
    SecurityIncidentCreated,
    SecurityIncidentUpdated,
    SecurityIncidentResolved,
)
from app.context.security.domain.exceptions.security_exceptions import (
    CannotModifyResolvedIncidentException,
)


@dataclass
class SecurityIncident(AggregateRoot):
    """Корень агрегата инцидента безопасности (Security BC)."""

    title: str = ""
    event_type: SecurityEventType = SecurityEventType.OTHER
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    status: IncidentStatus = IncidentStatus.OPEN
    description: str | None = None
    affected_resource_type: AuditResource | None = None
    affected_resource_id: Id | None = None
    actor_id: Id | None = None
    notes: list[IncidentNote] = field(default_factory=list)
    resolved_by: Id | None = None
    resolution: str | None = None
    workspace_id: Id | None = None
    detected_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    resolved_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create(
        cls,
        title: str,
        event_type: SecurityEventType,
        severity: IncidentSeverity,
        workspace_id: Id | None = None,
        description: str | None = None,
        affected_resource_type: AuditResource | None = None,
        affected_resource_id: Id | None = None,
        actor_id: Id | None = None,
    ) -> SecurityIncident:
        incident = cls(
            title=title,
            event_type=event_type,
            severity=severity,
            workspace_id=workspace_id,
            description=description,
            affected_resource_type=affected_resource_type,
            affected_resource_id=affected_resource_id,
            actor_id=actor_id,
        )
        incident._register_event(
            SecurityIncidentCreated(incident_id=str(incident.id), severity=severity)
        )
        return incident

    def _assert_can_modify(self) -> None:
        if self.status in (IncidentStatus.RESOLVED, IncidentStatus.FALSE_POSITIVE):
            raise CannotModifyResolvedIncidentException()

    def start_investigation(self, investigator_id: Id) -> None:
        self._assert_can_modify()
        if self.status != IncidentStatus.OPEN:
            return
        self.status = IncidentStatus.INVESTIGATING
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(SecurityIncidentUpdated(incident_id=str(self.id), changed_fields=["status"]))

    def mitigate(self, mitigator_id: Id) -> None:
        self._assert_can_modify()
        if self.status != IncidentStatus.INVESTIGATING:
            return
        self.status = IncidentStatus.MITIGATED
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(SecurityIncidentUpdated(incident_id=str(self.id), changed_fields=["status"]))

    def resolve(self, resolved_by: Id, resolution: str) -> None:
        self._assert_can_modify()
        if self.status not in (IncidentStatus.INVESTIGATING, IncidentStatus.MITIGATED):
            return
        self.status = IncidentStatus.RESOLVED
        self.resolved_by = resolved_by
        self.resolution = resolution
        self.resolved_at = datetime.now(tz=timezone.utc)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            SecurityIncidentResolved(incident_id=str(self.id), resolved_by=str(resolved_by), resolution=resolution)
        )

    def mark_false_positive(self, resolved_by: Id) -> None:
        self._assert_can_modify()
        self.status = IncidentStatus.FALSE_POSITIVE
        self.resolved_by = resolved_by
        self.resolved_at = datetime.now(tz=timezone.utc)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(SecurityIncidentUpdated(incident_id=str(self.id), changed_fields=["status"]))

    def add_note(self, author_id: Id, content: str) -> None:
        note = IncidentNote(author_id=author_id, content=content)
        self.notes.append(note)
        self.updated_at = datetime.now(tz=timezone.utc)

    def update_severity(self, new_severity: IncidentSeverity) -> None:
        self._assert_can_modify()
        self.severity = new_severity
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(SecurityIncidentUpdated(incident_id=str(self.id), changed_fields=["severity"]))
