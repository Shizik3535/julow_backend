from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.dto.task_dto import TaskDTO
from app.context.task.application.ports.integration.outboard.task_provider import TaskProvider
from app.context.task.domain.repositories.task_repository import TaskRepository


class TaskProviderAdapter(TaskProvider):
    """
    Реализация outboard-порта TaskProvider.

    Предоставляет данные задач другим BC через TaskRepository.
    """

    def __init__(self, repo: TaskRepository) -> None:
        self._repo = repo

    async def task_exists(self, task_id: str) -> bool:
        task = await self._repo.get_by_id(Id.from_string(task_id))
        return task is not None

    async def get_task(self, task_id: str) -> TaskDTO | None:
        task = await self._repo.get_by_id(Id.from_string(task_id))
        if task is None:
            return None
        return self._to_dto(task)

    async def get_tasks_by_project(self, project_id: str) -> list[TaskDTO]:
        tasks = await self._repo.get_by_project(Id.from_string(project_id))
        return [self._to_dto(t) for t in tasks]

    async def count_by_project(self, project_id: str) -> int:
        return await self._repo.count_by_project(Id.from_string(project_id))

    # ------------------------------------------------------------------
    # Helper: Task → TaskDTO
    # ------------------------------------------------------------------

    @staticmethod
    def _to_dto(task) -> TaskDTO:
        description = None
        if task.description is not None:
            description = {
                "content": task.description.content,
                "format": task.description.format.value,
            }

        effort_estimate = None
        if task.effort_estimate is not None:
            effort_estimate = {
                "value": task.effort_estimate.value,
                "unit": task.effort_estimate.unit.value,
            }

        actual_effort = None
        if task.actual_effort is not None:
            actual_effort = {
                "value": task.actual_effort.value,
                "unit": task.actual_effort.unit.value,
            }

        order = None
        if task.order is not None:
            order = {
                "position": task.order.position,
                "column_id": str(task.order.column_id),
            }

        recurrence = None
        if task.recurrence is not None:
            recurrence = {
                "pattern": task.recurrence.pattern.value,
                "interval": task.recurrence.interval,
                "end_date": str(task.recurrence.end_date) if task.recurrence.end_date else None,
                "max_occurrences": task.recurrence.max_occurrences,
            }

        labels = []
        for label in task.labels:
            label_dict: dict[str, str | None] = {"name": label.name}
            if label.color is not None:
                label_dict["color"] = str(label.color)
            labels.append(label_dict)

        checklists = []
        for cl in task.checklists:
            items = []
            for item in cl.items:
                items.append({
                    "id": str(item.id),
                    "text": item.text,
                    "is_checked": item.is_checked,
                    "assignee_id": str(item.assignee_id) if item.assignee_id else None,
                    "due_date": str(item.due_date) if item.due_date else None,
                    "checked_at": item.checked_at.isoformat() if item.checked_at else None,
                    "order": item.order,
                })
            checklists.append({
                "id": str(cl.id),
                "title": cl.title,
                "items": items,
            })

        relations = []
        for r in task.relations:
            relations.append({
                "id": str(r.id),
                "related_task_id": str(r.related_task_id),
                "relation_type": r.relation_type.value,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "created_by": str(r.created_by),
            })

        watchers = []
        for w in task.watchers:
            watchers.append({
                "id": str(w.id),
                "user_id": str(w.user_id),
                "watched_at": w.watched_at.isoformat() if w.watched_at else None,
            })

        attachments = []
        for a in task.attachments:
            attachments.append({
                "id": str(a.id),
                "file_id": str(a.file_id),
                "filename": a.filename,
                "size_bytes": a.size_bytes,
                "uploaded_by": str(a.uploaded_by),
                "uploaded_at": a.uploaded_at.isoformat() if a.uploaded_at else None,
            })

        return TaskDTO(
            id=str(task.id),
            project_id=str(task.project_id),
            parent_task_id=str(task.parent_task_id) if task.parent_task_id else None,
            epic_id=str(task.epic_id) if task.epic_id else None,
            title=task.title,
            description=description,
            status_id=str(task.status_id) if task.status_id else None,
            priority=task.priority.value,
            task_type=task.task_type.value,
            assignee_ids=[str(uid) for uid in task.assignee_ids],
            reporter_id=str(task.reporter_id) if task.reporter_id else None,
            labels=labels,
            progress=task.progress.value,
            effort_estimate=effort_estimate,
            actual_effort=actual_effort,
            start_date=str(task.start_date) if task.start_date else None,
            due_date=str(task.due_date) if task.due_date else None,
            completed_at=task.completed_at,
            custom_fields=task.custom_fields,
            checklists=checklists,
            relations=relations,
            watchers=watchers,
            attachments=attachments,
            order=order,
            sprint_id=str(task.sprint_id) if task.sprint_id else None,
            status=task.status.value,
            recurrence=recurrence,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
