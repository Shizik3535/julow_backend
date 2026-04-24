from __future__ import annotations

from abc import abstractmethod
from datetime import date
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.timetracking.domain.aggregates.time_entry import TimeEntry
from app.context.timetracking.domain.value_objects.time_entry_status import TimeEntryStatus


class TimeEntryRepository(RepositoryPort[TimeEntry]):
    """Порт репозитория для агрегата TimeEntry."""

    @abstractmethod
    async def get_by_user(self, user_id: Id) -> list[TimeEntry]:
        """Найти записи пользователя."""

    @abstractmethod
    async def get_by_user_and_date(self, user_id: Id, entry_date: date) -> list[TimeEntry]:
        """Найти записи пользователя за дату."""

    @abstractmethod
    async def get_by_task(self, task_id: Id) -> list[TimeEntry]:
        """Найти записи по задаче."""

    @abstractmethod
    async def get_by_project(self, project_id: Id) -> list[TimeEntry]:
        """Найти записи по проекту."""

    @abstractmethod
    async def get_by_epic(self, epic_id: Id) -> list[TimeEntry]:
        """Найти записи по эпику."""

    @abstractmethod
    async def get_by_workspace(self, workspace_id: Id) -> list[TimeEntry]:
        """Найти записи workspace."""

    @abstractmethod
    async def get_running_timer(self, user_id: Id) -> TimeEntry | None:
        """Найти запущенный таймер пользователя."""

    @abstractmethod
    async def get_by_status(self, workspace_id: Id, status: TimeEntryStatus) -> list[TimeEntry]:
        """Найти записи по статусу."""

    @abstractmethod
    async def get_submitted_for_approval(self, workspace_id: Id) -> list[TimeEntry]:
        """Найти записи со статусом SUBMITTED для менеджера."""

    @abstractmethod
    async def get_by_category(self, category_id: Id) -> list[TimeEntry]:
        """Найти записи по категории."""

    @abstractmethod
    async def sum_duration_by_user(self, user_id: Id, start: date, end: date) -> int:
        """Суммарная длительность записей пользователя за период."""

    @abstractmethod
    async def sum_duration_by_project(self, project_id: Id, start: date, end: date) -> int:
        """Суммарная длительность записей по проекту за период."""

    @abstractmethod
    async def search(self, offset: int = 0, limit: int = 100, filters: dict[str, Any] | None = None) -> list[TimeEntry]:
        """Поиск записей."""
