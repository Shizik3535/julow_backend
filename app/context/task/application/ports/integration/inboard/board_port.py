from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BoardPort(ABC):
    """
    Inboard-порт: получение данных доски из Project BC (Board AR).

    Используется для:
    - Получения workflow-статусов.
    - Валидации переходов статусов.
    - Получения колонок доски.
    - Default status для новых задач.
    """

    @abstractmethod
    async def get_workflow_statuses(self, project_id: str) -> list[dict[str, Any]]:
        """Получить workflow-статусы проекта."""

    @abstractmethod
    async def get_default_status_id(self, project_id: str) -> str | None:
        """Получить ID статуса по умолчанию."""

    @abstractmethod
    async def is_transition_allowed(
        self, project_id: str, from_status_id: str, to_status_id: str
    ) -> bool:
        """Проверить, разрешён ли переход между статусами."""

    @abstractmethod
    async def get_columns(self, project_id: str) -> list[dict[str, Any]]:
        """Получить колонки доски."""
