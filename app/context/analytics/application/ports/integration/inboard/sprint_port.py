from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class SprintMeta:
    """Минимальная sprint-метаинформация для аналитических расчётов.

    Используется ``TaskAnalyticsResolver`` для построения burndown:
    нужны ``sprint_start``/``sprint_end`` и ``project_id``, чтобы
    скомбинировать с counts от Task BC.
    """

    id: str
    project_id: str
    name: str
    status: str
    sprint_start: date | None
    sprint_end: date | None


class SprintPort(ABC):
    """Inboard-порт Analytics BC: метаданные спринтов из Project BC."""

    @abstractmethod
    async def get_sprint_meta(self, sprint_id: str) -> SprintMeta | None:
        """Получить метаданные спринта по ID."""

    @abstractmethod
    async def get_active_sprint_meta(self, project_id: str) -> SprintMeta | None:
        """Получить активный спринт проекта."""
