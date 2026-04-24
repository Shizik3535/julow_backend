from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.context.project.application.dto.board_dto import BoardDTO


class BoardProvider(ABC):
    """
    Outboard-порт: предоставление данных доски другим BC.

    Task BC использует для:
    - Получения workflow-статусов проекта (назначение статуса задаче).
    - Валидации переходов (task status change).
    - Получения колонок (позиционирование задач на доске).
    """

    @abstractmethod
    async def get_board(self, project_id: str) -> BoardDTO | None:
        """Получить доску проекта."""

    @abstractmethod
    async def get_workflow_statuses(self, project_id: str) -> list[dict[str, Any]]:
        """Получить workflow-статусы проекта (list[dict])."""

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
