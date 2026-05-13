from __future__ import annotations

from app.context.task.application.ports.integration.outboard.task_provider import TaskProvider
from app.context.timetracking.application.ports.integration.inboard.task_port import TaskPort


class TaskAdapter(TaskPort):
    """Inboard TaskPort для TimeTracking BC. Делегирует в outboard Task BC."""

    def __init__(self, task_provider: TaskProvider) -> None:
        self._provider = task_provider

    async def task_exists(self, task_id: str) -> bool:
        return await self._provider.task_exists(task_id)

    async def get_task_project_id(self, task_id: str) -> str | None:
        dto = await self._provider.get_task(task_id)
        if dto is None:
            return None
        return getattr(dto, "project_id", None)
