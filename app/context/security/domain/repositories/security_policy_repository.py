from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.security.domain.aggregates.security_policy import SecurityPolicy


class SecurityPolicyRepository(RepositoryPort[SecurityPolicy]):
    @abstractmethod
    async def get_by_workspace(self, workspace_id: Id) -> SecurityPolicy | None: ...

    @abstractmethod
    async def get_by_organization(self, organization_id: Id) -> SecurityPolicy | None: ...

    @abstractmethod
    async def get_global(self) -> SecurityPolicy | None: ...

    @abstractmethod
    async def search(self, offset: int = 0, limit: int = 100, filters: dict[str, Any] | None = None) -> list[SecurityPolicy]: ...
