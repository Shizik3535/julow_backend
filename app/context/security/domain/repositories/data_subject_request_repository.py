from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.security.domain.aggregates.data_subject_request import DataSubjectRequest
from app.context.security.domain.value_objects.data_subject_request_status import DataSubjectRequestStatus
from app.context.security.domain.value_objects.data_subject_request_type import DataSubjectRequestType


class DataSubjectRequestRepository(RepositoryPort[DataSubjectRequest]):
    @abstractmethod
    async def get_by_user(self, user_id: Id) -> list[DataSubjectRequest]: ...

    @abstractmethod
    async def get_by_status(self, status: DataSubjectRequestStatus) -> list[DataSubjectRequest]: ...

    @abstractmethod
    async def get_overdue(self) -> list[DataSubjectRequest]: ...

    @abstractmethod
    async def get_by_type(self, request_type: DataSubjectRequestType) -> list[DataSubjectRequest]: ...

    @abstractmethod
    async def search(self, offset: int = 0, limit: int = 100, filters: dict[str, Any] | None = None) -> list[DataSubjectRequest]: ...
