from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.communication.domain.aggregates.meeting import Meeting
from app.context.communication.domain.value_objects.meeting_status import MeetingStatus


class MeetingRepository(RepositoryPort[Meeting]):
    """Порт репозитория для агрегата Meeting."""

    @abstractmethod
    async def get_by_workspace(self, workspace_id: Id) -> list[Meeting]:
        """Найти совещания workspace."""

    @abstractmethod
    async def get_by_project(self, project_id: Id) -> list[Meeting]:
        """Найти совещания проекта."""

    @abstractmethod
    async def get_upcoming_by_participant(self, user_id: Id) -> list[Meeting]:
        """Найти предстоящие совещания участника."""

    @abstractmethod
    async def get_by_organizer(self, organizer_id: Id) -> list[Meeting]:
        """Найти совещания организатора."""

    @abstractmethod
    async def get_by_status(self, workspace_id: Id, status: MeetingStatus) -> list[Meeting]:
        """Найти совещания по статусу."""

    @abstractmethod
    async def search(self, offset: int = 0, limit: int = 100, filters: dict[str, Any] | None = None) -> list[Meeting]:
        """Поиск совещаний."""
