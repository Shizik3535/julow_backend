from __future__ import annotations

from typing import Any

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.dto.task_dto import TaskDTO
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.repositories.task_repository import TaskRepository
from app.context.task.domain.aggregates.task import Task


class GetTaskQuery(BaseQuery):
    """
    Запрос получения задачи по ID.

    Атрибуты:
        caller_id: ID пользователя, выполняющего запрос.
        task_id: Идентификатор задачи.
    """

    caller_id: str
    task_id: str


class GetTaskHandler(BaseQueryHandler[GetTaskQuery, TaskDTO]):
    """Обработчик получения задачи по ID."""

    REQUIRED_PERMISSION = "tasks.read"

    def __init__(
        self,
        task_repo: TaskRepository,
        permission_checker: TaskPermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetTaskQuery) -> TaskDTO:
        task = await self._task_repo.get_by_id(Id.from_string(query.task_id))
        if task is None:
            raise TaskNotFoundException(id=query.task_id)
        await self._permission_checker.require_permission(
            user_id=query.caller_id,
            project_id=str(task.project_id),
            permission=self.REQUIRED_PERMISSION,
        )
        return _map_task_to_dto(task)


def _map_task_to_dto(task: Task) -> TaskDTO:
    """Маппинг доменного Task в TaskDTO."""
    labels: list[dict[str, Any]] = [
        {"name": lb.name, "color": lb.color.hex if lb.color else None}
        for lb in task.labels
    ]
    checklists: list[dict[str, Any]] = [
        {
            "id": str(cl.id),
            "title": cl.title,
            "items": [
                {
                    "id": str(item.id),
                    "text": item.text,
                    "is_checked": item.is_checked,
                    "assignee_id": str(item.assignee_id) if item.assignee_id else None,
                    "due_date": str(item.due_date) if item.due_date else None,
                    "checked_at": item.checked_at.isoformat() if item.checked_at else None,
                    "order": item.order,
                }
                for item in cl.items
            ],
        }
        for cl in task.checklists
    ]
    relations: list[dict[str, Any]] = [
        {
            "related_task_id": str(r.related_task_id),
            "relation_type": r.relation_type.value,
            "created_at": r.created_at.isoformat(),
            "created_by": str(r.created_by),
        }
        for r in task.relations
    ]
    watchers: list[dict[str, Any]] = [
        {"user_id": str(w.user_id), "watched_at": w.watched_at.isoformat()}
        for w in task.watchers
    ]
    attachments: list[dict[str, Any]] = [
        {
            "file_id": str(a.file_id),
            "filename": a.filename,
            "size_bytes": a.size_bytes,
            "uploaded_by": str(a.uploaded_by),
            "uploaded_at": a.uploaded_at.isoformat(),
        }
        for a in task.attachments
    ]
    order_dict: dict[str, Any] | None = None
    if task.order:
        order_dict = {
            "position": task.order.position,
            "column_id": str(task.order.column_id) if task.order.column_id else None,
        }
    effort_est: dict[str, Any] | None = None
    if task.effort_estimate:
        effort_est = {"value": task.effort_estimate.value, "unit": task.effort_estimate.unit.value}
    actual_eff: dict[str, Any] | None = None
    if task.actual_effort:
        actual_eff = {"value": task.actual_effort.value, "unit": task.actual_effort.unit.value}
    recurrence: dict[str, Any] | None = None
    if task.recurrence:
        recurrence = {
            "pattern": task.recurrence.pattern.value,
            "interval": task.recurrence.interval,
            "end_date": str(task.recurrence.end_date) if task.recurrence.end_date else None,
            "max_occurrences": task.recurrence.max_occurrences,
        }

    return TaskDTO(
        id=str(task.id),
        project_id=str(task.project_id),
        parent_task_id=str(task.parent_task_id) if task.parent_task_id else None,
        epic_id=str(task.epic_id) if task.epic_id else None,
        title=task.title,
        description={"content": task.description.content, "format": task.description.format.value} if task.description else None,
        status_id=str(task.status_id) if task.status_id else None,
        priority=task.priority.value,
        task_type=task.task_type.value,
        assignee_ids=[str(a) for a in task.assignee_ids],
        reporter_id=str(task.reporter_id) if task.reporter_id else None,
        labels=labels,
        progress=task.progress.value,
        effort_estimate=effort_est,
        actual_effort=actual_eff,
        start_date=str(task.start_date) if task.start_date else None,
        due_date=str(task.due_date) if task.due_date else None,
        completed_at=task.completed_at,
        custom_fields=task.custom_fields,
        checklists=checklists,
        relations=relations,
        watchers=watchers,
        attachments=attachments,
        order=order_dict,
        sprint_id=str(task.sprint_id) if task.sprint_id else None,
        status=task.status.value,
        recurrence=recurrence,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )
