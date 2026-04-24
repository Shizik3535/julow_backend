from __future__ import annotations

from abc import abstractmethod

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.aggregates.changelog import ChangelogEntry


class ChangelogRepository(RepositoryPort[ChangelogEntry]):
    """
    Порт репозитория для агрегата ChangelogEntry.

    Записи истории изменений не загружаются полностью в Task AR.
    Доступ через пагинацию.
    """

    @abstractmethod
    async def get_by_task_id(self, task_id: Id, offset: int = 0, limit: int = 50) -> list[ChangelogEntry]:
        """Получить историю изменений задачи с пагинацией."""

    @abstractmethod
    async def get_by_task_and_field(self, task_id: Id, field_name: str) -> list[ChangelogEntry]:
        """Получить историю изменений конкретного поля."""

    @abstractmethod
    async def get_recent_changes(self, task_id: Id, limit: int = 10) -> list[ChangelogEntry]:
        """Получить последние изменения задачи."""

    @abstractmethod
    async def count_by_task(self, task_id: Id) -> int:
        """Подсчитать количество записей истории для задачи."""
