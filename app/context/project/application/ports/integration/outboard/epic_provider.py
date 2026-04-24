from __future__ import annotations

from abc import ABC, abstractmethod

from app.context.project.application.dto.epic_dto import EpicDTO


class EpicProvider(ABC):
    """
    Outboard-порт: предоставление данных эпиков другим BC.

    Task BC использует для:
    - Проверки существования эпика (привязка задачи к эпику).
    - Получения эпиков проекта (группировка задач).
    """

    @abstractmethod
    async def epic_exists(self, epic_id: str) -> bool:
        """Проверить существование эпика."""

    @abstractmethod
    async def get_epic(self, epic_id: str) -> EpicDTO | None:
        """Получить эпик по ID."""

    @abstractmethod
    async def get_epics_by_project(self, project_id: str) -> list[EpicDTO]:
        """Получить все эпики проекта."""
