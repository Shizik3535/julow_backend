from __future__ import annotations

from app.context.task.application.ports.integration.outboard.task_participant_provider import (
    TaskParticipantProvider,
)
from app.context.notification.application.ports.integration.inboard.task_participant_port import (
    TaskParticipantPort,
)


class TaskParticipantAdapter(TaskParticipantPort):
    """
    Реализация inboard-порта TaskParticipantPort для Notification BC.

    Делегирует получение участников задачи в outboard-порт
    Task BC (TaskParticipantProvider).
    """

    def __init__(self, task_participant_provider: TaskParticipantProvider) -> None:
        self._provider = task_participant_provider

    async def get_task_participants(self, task_id: str) -> list[str]:
        return await self._provider.get_task_participants(task_id=task_id)

    async def get_task_assignees(self, task_id: str) -> list[str]:
        return await self._provider.get_task_assignees(task_id=task_id)
