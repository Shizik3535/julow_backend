from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.ip_address_vo import IpAddress
from app.context.security.domain.value_objects.audit_action import AuditAction
from app.context.security.domain.value_objects.audit_resource import AuditResource
from app.context.security.domain.value_objects.severity import Severity
from app.context.security.domain.events.audit_events import AuditEntryCreated


@dataclass
class AuditLog(AggregateRoot):
    """Корень агрегата записи аудита (Security BC). Immutable — только create."""

    actor_id: Id | None = None
    action: AuditAction = AuditAction.READ
    resource_type: AuditResource = AuditResource.SYSTEM
    resource_id: Id | None = None
    ip_address: IpAddress | None = None
    user_agent: str | None = None
    severity: Severity = Severity.INFO
    details: dict[str, str] = field(default_factory=dict)
    workspace_id: Id | None = None
    organization_id: Id | None = None
    occurred_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create(
        cls,
        action: AuditAction,
        resource_type: AuditResource,
        severity: Severity = Severity.INFO,
        actor_id: Id | None = None,
        resource_id: Id | None = None,
        ip_address: IpAddress | None = None,
        user_agent: str | None = None,
        details: dict[str, str] | None = None,
        workspace_id: Id | None = None,
        organization_id: Id | None = None,
    ) -> AuditLog:
        log = cls(
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            severity=severity,
            details=details or {},
            workspace_id=workspace_id,
            organization_id=organization_id,
        )
        log._register_event(
            AuditEntryCreated(
                actor_id=str(actor_id) if actor_id else "",
                action=action,
                resource_type=resource_type,
                resource_id=str(resource_id) if resource_id else "",
                severity=severity,
            )
        )
        return log
