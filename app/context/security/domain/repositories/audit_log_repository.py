from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.security.domain.aggregates.audit_log import AuditLog
from app.context.security.domain.value_objects.audit_action import AuditAction
from app.context.security.domain.value_objects.audit_resource import AuditResource


class AuditLogRepository(RepositoryPort[AuditLog]):
    @abstractmethod
    async def get_by_actor(self, actor_id: Id) -> list[AuditLog]: ...

    @abstractmethod
    async def get_by_resource(self, resource_type: AuditResource, resource_id: Id | None = None) -> list[AuditLog]: ...

    @abstractmethod
    async def get_by_workspace(self, workspace_id: Id) -> list[AuditLog]: ...

    @abstractmethod
    async def get_by_organization(self, organization_id: Id) -> list[AuditLog]: ...

    @abstractmethod
    async def get_by_action(self, action: AuditAction) -> list[AuditLog]: ...

    @abstractmethod
    async def get_by_date_range(self, start: datetime, end: datetime) -> list[AuditLog]: ...

    @abstractmethod
    async def search(self, offset: int = 0, limit: int = 100, filters: dict[str, Any] | None = None) -> list[AuditLog]: ...

    @abstractmethod
    async def get_suspicious_activity(self, actor_id: Id | None = None, since: datetime | None = None) -> list[AuditLog]: ...

    @abstractmethod
    async def count_by_action(self, action: AuditAction, since: datetime | None = None) -> int: ...
