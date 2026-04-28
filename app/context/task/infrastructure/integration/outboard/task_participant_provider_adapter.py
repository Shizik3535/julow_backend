from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.ports.integration.outboard.task_participant_provider import (
    TaskParticipantProvider,
)
from app.context.task.domain.repositories.task_repository import TaskRepository


class TaskParticipantProviderAdapter(TaskParticipantProvider):
    """
    Реализация outboard-порта TaskParticipantProvider.

    Предоставляет данные участников задачи другим BC через TaskRepository.
    """

    def __init__(self, repo: TaskRepository) -> None:
        self._repo = repo

    async def get_task_participants(self, task_id: str) -> list[str]:
        task = await self._repo.get_by_id(Id.from_string(task_id))
        if task is None:
            return []

        participant_ids: set[str] = set()

        for uid in task.assignee_ids:
            participant_ids.add(str(uid))

        for watcher in task.watchers:
            participant_ids.add(str(watcher.user_id))

        if task.reporter_id is not None:
            participant_ids.add(str(task.reporter_id))

        return list(participant_ids)

    async def get_task_assignees(self, task_id: str) -> list[str]:
        task = await self._repo.get_by_id(Id.from_string(task_id))
        if task is None:
            return []

        return [str(uid) for uid in task.assignee_ids]
