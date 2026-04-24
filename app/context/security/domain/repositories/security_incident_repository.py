from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.security.domain.aggregates.security_incident import SecurityIncident
from app.context.security.domain.value_objects.incident_status import IncidentStatus
from app.context.security.domain.value_objects.incident_severity import IncidentSeverity
from app.context.security.domain.value_objects.security_event_type import SecurityEventType


class SecurityIncidentRepository(RepositoryPort[SecurityIncident]):
    @abstractmethod
    async def get_by_workspace(self, workspace_id: Id) -> list[SecurityIncident]: ...

    @abstractmethod
    async def get_by_status(self, status: IncidentStatus, workspace_id: Id | None = None) -> list[SecurityIncident]: ...

    @abstractmethod
    async def get_by_severity(self, severity: IncidentSeverity, workspace_id: Id | None = None) -> list[SecurityIncident]: ...

    @abstractmethod
    async def get_by_event_type(self, event_type: SecurityEventType, workspace_id: Id | None = None) -> list[SecurityIncident]: ...

    @abstractmethod
    async def search(self, offset: int = 0, limit: int = 100, filters: dict[str, Any] | None = None) -> list[SecurityIncident]: ...

    @abstractmethod
    async def count_open(self, workspace_id: Id | None = None) -> int: ...
