from __future__ import annotations

from collections import defaultdict
from datetime import date

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.application.base_dto import BaseDTO
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
from app.context.task.domain.aggregates.task import Task
from app.context.task.domain.repositories.task_repository import TaskRepository
from app.context.task.domain.value_objects.relation_type import RelationType


class CriticalPathNodeDTO(BaseDTO):
    """
    Узел критического пути.

    Атрибуты:
        task_id: ID задачи.
        title: Заголовок задачи.
        start_date: Дата начала (ISO).
        due_date: Дедлайн (ISO).
        duration_days: Длительность в днях.
        slack_days: Запас времени (float of slack = 0 → на критическом пути).
    """

    task_id: str
    title: str
    start_date: str | None = None
    due_date: str | None = None
    duration_days: int = 0
    slack_days: float = 0.0


class CriticalPathDTO(BaseDTO):
    """
    Результат расчёта критического пути.

    Атрибуты:
        path: Упорядоченный список узлов на критическом пути.
        total_duration_days: Общая длительность критического пути в днях.
    """

    path: list[CriticalPathNodeDTO]
    total_duration_days: int = 0


class GetCriticalPathQuery(BaseQuery):
    """
    Запрос расчёта критического пути проекта.

    Атрибуты:
        caller_id: ID пользователя.
        project_id: ID проекта.
    """

    caller_id: str
    project_id: str


class GetCriticalPathHandler(BaseQueryHandler[GetCriticalPathQuery, CriticalPathDTO]):
    """
    Обработчик расчёта критического пути (CPM).

    Строит DAG из BLOCKS-связей задач проекта, выполняет
    forward/backward pass и возвращает узлы с нулевым slack.
    """

    REQUIRED_PERMISSION = "tasks.read"

    def __init__(
        self,
        task_repo: TaskRepository,
        permission_checker: TaskPermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetCriticalPathQuery) -> CriticalPathDTO:
        await self._permission_checker.require_permission(
            user_id=query.caller_id,
            project_id=query.project_id,
            permission=self.REQUIRED_PERMISSION,
        )

        all_tasks = await self._task_repo.get_by_project(Id.from_string(query.project_id))
        active_tasks = [t for t in all_tasks if t.status.value.lower() == "active"]

        return self._compute_critical_path(active_tasks)

    def _compute_critical_path(self, tasks: list[Task]) -> CriticalPathDTO:
        task_map: dict[str, Task] = {str(t.id): t for t in tasks}
        valid_ids = set(task_map.keys())

        durations: dict[str, int] = {}
        for tid, task in task_map.items():
            if task.start_date and task.due_date:
                durations[tid] = max((task.due_date - task.start_date).days, 0)
            else:
                durations[tid] = 0

        successors: dict[str, list[str]] = defaultdict(list)
        predecessors: dict[str, list[str]] = defaultdict(list)

        for tid, task in task_map.items():
            for rel in task.relations:
                related_id = str(rel.related_task_id)
                if related_id not in valid_ids:
                    continue
                if rel.relation_type == RelationType.BLOCKS:
                    successors[tid].append(related_id)
                    predecessors[related_id].append(tid)
                elif rel.relation_type == RelationType.IS_BLOCKED_BY:
                    successors[related_id].append(tid)
                    predecessors[tid].append(related_id)

        if not task_map:
            return CriticalPathDTO(path=[], total_duration_days=0)

        es: dict[str, float] = {}
        ef: dict[str, float] = {}

        topo_order = self._topological_sort(valid_ids, successors, predecessors)
        if not topo_order:
            return CriticalPathDTO(path=[], total_duration_days=0)

        for tid in topo_order:
            if predecessors[tid]:
                es[tid] = max(ef[p] for p in predecessors[tid] if p in ef)
            else:
                es[tid] = 0.0
            ef[tid] = es[tid] + durations[tid]

        project_end = max(ef.values()) if ef else 0.0

        lf: dict[str, float] = {}
        ls: dict[str, float] = {}

        for tid in reversed(topo_order):
            if successors[tid]:
                lf[tid] = min(ls[s] for s in successors[tid] if s in ls)
            else:
                lf[tid] = project_end
            ls[tid] = lf[tid] - durations[tid]

        slack: dict[str, float] = {}
        for tid in topo_order:
            slack[tid] = ls.get(tid, 0.0) - es.get(tid, 0.0)

        critical_ids = [tid for tid in topo_order if abs(slack[tid]) < 0.001]

        path: list[CriticalPathNodeDTO] = []
        for tid in critical_ids:
            task = task_map[tid]
            path.append(
                CriticalPathNodeDTO(
                    task_id=tid,
                    title=task.title,
                    start_date=str(task.start_date) if task.start_date else None,
                    due_date=str(task.due_date) if task.due_date else None,
                    duration_days=durations[tid],
                    slack_days=slack[tid],
                )
            )

        total = int(project_end) if project_end else 0
        return CriticalPathDTO(path=path, total_duration_days=total)

    @staticmethod
    def _topological_sort(
        ids: set[str],
        successors: dict[str, list[str]],
        predecessors: dict[str, list[str]],
    ) -> list[str]:
        """Алгоритм Кана для топологической сортировки DAG."""
        in_degree: dict[str, int] = {tid: 0 for tid in ids}
        for tid in ids:
            for succ in successors.get(tid, []):
                if succ in in_degree:
                    in_degree[succ] += 1

        queue = [tid for tid in ids if in_degree[tid] == 0]
        queue.sort()
        result: list[str] = []

        while queue:
            node = queue.pop(0)
            result.append(node)
            for succ in successors.get(node, []):
                if succ in in_degree:
                    in_degree[succ] -= 1
                    if in_degree[succ] == 0:
                        queue.append(succ)

        if len(result) != len(ids):
            return []

        return result
