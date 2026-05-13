from __future__ import annotations

from abc import ABC, abstractmethod


class EpicPort(ABC):
    """
    Inboard-порт: получение данных эпика из Project BC.

    TimeTracking BC использует для проверки существования эпика при
    привязке записи времени.
    """

    @abstractmethod
    async def epic_exists(self, epic_id: str) -> bool:
        """Проверить существование эпика."""
