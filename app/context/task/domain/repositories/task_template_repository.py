from __future__ import annotations

from abc import abstractmethod

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.aggregates.task_template import TaskTemplate


class TaskTemplateRepository(RepositoryPort[TaskTemplate]):
    """Порт репозитория для агрегата TaskTemplate."""

    @abstractmethod
    async def get_by_project(self, project_id: Id) -> list[TaskTemplate]:
        """Получить шаблоны проекта."""

    @abstractmethod
    async def get_system_templates(self) -> list[TaskTemplate]:
        """Получить все системные шаблоны."""

    @abstractmethod
    async def get_by_name(self, name: str) -> TaskTemplate | None:
        """Найти шаблон по названию."""
