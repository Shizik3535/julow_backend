from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_domain_event import BaseDomainEvent
from app.context.security.domain.value_objects.audit_action import AuditAction
from app.context.security.domain.value_objects.audit_resource import AuditResource
from app.context.security.domain.value_objects.severity import Severity


@dataclass(frozen=True)
class AuditEntryCreated(BaseDomainEvent):
    actor_id: str = ""
    action: AuditAction = AuditAction.READ
    resource_type: AuditResource = AuditResource.SYSTEM
    resource_id: str = ""
    severity: Severity = Severity.INFO
