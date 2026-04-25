from __future__ import annotations

from datetime import date as date_type

from typing import Any

from sqlalchemy import and_, func, select, type_coerce
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.exceptions.entity_not_found_exception import EntityNotFoundException
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.task.domain.aggregates.task import Task
from app.context.task.domain.repositories.task_repository import TaskRepository
from app.context.task.domain.value_objects.label import Label
from app.context.task.infrastructure.persistence.mappers.task_mapper import TaskMapper
from app.context.task.infrastructure.persistence.orm_models.task_orm import (
    TaskAttachmentORM,
    TaskChecklistItemORM,
    TaskChecklistORM,
    TaskORM,
    TaskRelationORM,
    TaskWatcherORM,
    task_labels_table,
)


class SqlTaskRepository(SqlAlchemyRepository[Task, TaskORM], TaskRepository):
    """SQLAlchemy-реализация TaskRepository."""

    def __init__(self, session: AsyncSession, mapper: TaskMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=TaskORM)

    # ------------------------------------------------------------------
    # Override add — labels через association table
    # ------------------------------------------------------------------

    async def add(self, aggregate: Task) -> Task:
        orm_model = self._mapper.to_orm(aggregate)
        self._session.add(orm_model)
        await self._session.flush()

        # Labels через association table
        for label in aggregate.labels:
            label_dict = self._mapper.label_to_dict(label)
            await self._session.execute(
                task_labels_table.insert().values(
                    task_id=orm_model.id,
                    label_name=label_dict["label_name"],
                    label_color=label_dict["label_color"],
                )
            )

        await self._session.flush()
        return aggregate

    # ------------------------------------------------------------------
    # Override update — синхронизация дочерних + labels
    # ------------------------------------------------------------------

    async def update(self, aggregate: Task) -> Task:
        uuid_val = self._mapper._map_uuid(aggregate.id)
        stmt = select(TaskORM).where(TaskORM.id == uuid_val)
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model is None:
            raise EntityNotFoundException(entity_type="Task", id=aggregate.id)

        # Обновить скалярные поля
        updated_orm = self._mapper.to_orm(aggregate)
        for column in TaskORM.__table__.columns:
            col_name = column.name
            if col_name in ("id", "created_at"):
                continue
            setattr(orm_model, col_name, getattr(updated_orm, col_name, None))

        # Синхронизация дочерних: delete old + insert new
        await self._session.execute(
            TaskChecklistItemORM.__table__.delete().where(
                TaskChecklistItemORM.checklist_id.in_(
                    select(TaskChecklistORM.id).where(TaskChecklistORM.task_id == uuid_val)
                )
            )
        )
        await self._session.execute(
            TaskChecklistORM.__table__.delete().where(TaskChecklistORM.task_id == uuid_val)
        )
        await self._session.execute(
            TaskRelationORM.__table__.delete().where(TaskRelationORM.task_id == uuid_val)
        )
        await self._session.execute(
            TaskWatcherORM.__table__.delete().where(TaskWatcherORM.task_id == uuid_val)
        )
        await self._session.execute(
            TaskAttachmentORM.__table__.delete().where(TaskAttachmentORM.task_id == uuid_val)
        )

        # Expunge old child objects from identity map to prevent conflicts
        # when new objects with the same PKs are added after bulk deletes.
        for cl in list(orm_model.checklists):
            for item in list(cl.items):
                self._session.expunge(item)
            self._session.expunge(cl)
        for rel in list(orm_model.relations):
            self._session.expunge(rel)
        for w in list(orm_model.watchers):
            self._session.expunge(w)
        for a in list(orm_model.attachments):
            self._session.expunge(a)

        for checklist in aggregate.checklists:
            cl_orm = self._mapper._checklist_to_orm(checklist, aggregate.id)
            self._session.add(cl_orm)
        for relation in aggregate.relations:
            rel_orm = self._mapper._relation_to_orm(relation, aggregate.id)
            self._session.add(rel_orm)
        for watcher in aggregate.watchers:
            w_orm = self._mapper._watcher_to_orm(watcher, aggregate.id)
            self._session.add(w_orm)
        for attachment in aggregate.attachments:
            a_orm = self._mapper._attachment_to_orm(attachment, aggregate.id)
            self._session.add(a_orm)

        # Синхронизация labels
        await self._session.execute(
            task_labels_table.delete().where(task_labels_table.c.task_id == uuid_val)
        )
        for label in aggregate.labels:
            label_dict = self._mapper.label_to_dict(label)
            await self._session.execute(
                task_labels_table.insert().values(
                    task_id=uuid_val,
                    label_name=label_dict["label_name"],
                    label_color=label_dict["label_color"],
                )
            )

        await self._session.flush()
        return aggregate

    # ------------------------------------------------------------------
    # Helper: загрузить labels для ORM-объекта
    # ------------------------------------------------------------------

    async def _load_labels(self, orm_model: TaskORM) -> list[Label]:
        """Загрузить labels из association table и прикрепить к ORM."""
        stmt = select(task_labels_table).where(task_labels_table.c.task_id == orm_model.id)
        result = await self._session.execute(stmt)
        rows = result.fetchall()
        labels = [self._mapper.dict_to_label({"label_name": r.label_name, "label_color": r.label_color}) for r in rows]
        orm_model._loaded_labels = labels  # type: ignore[attr-defined]
        return labels

    # ------------------------------------------------------------------
    # Helper: to_domain с подгрузкой labels
    # ------------------------------------------------------------------

    async def _to_domain_with_labels(self, orm_model: TaskORM) -> Task:
        """Преобразовать ORM → Domain с подгрузкой labels."""
        await self._load_labels(orm_model)
        return self._mapper.to_domain(orm_model)

    async def _to_domain_list_with_labels(self, orm_models: list[TaskORM]) -> list[Task]:
        """Преобразовать список ORM → Domain с подгрузкой labels."""
        result = []
        for orm in orm_models:
            await self._load_labels(orm)
            result.append(self._mapper.to_domain(orm))
        return result

    # ------------------------------------------------------------------
    # Override get_by_id — с подгрузкой labels
    # ------------------------------------------------------------------

    async def get_by_id(self, id: Id) -> Task | None:
        uuid_value = self._mapper._map_uuid(id)
        stmt = select(TaskORM).where(TaskORM.id == uuid_value)
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model is None:
            return None
        return await self._to_domain_with_labels(orm_model)

    # ------------------------------------------------------------------
    # Специфичные методы
    # ------------------------------------------------------------------

    async def get_by_project(self, project_id: Id) -> list[Task]:
        uuid_val = self._mapper._map_uuid(project_id)
        stmt = select(TaskORM).where(TaskORM.project_id == uuid_val)
        result = await self._session.execute(stmt)
        return await self._to_domain_list_with_labels(result.scalars().all())

    async def get_by_assignee(self, user_id: Id) -> list[Task]:
        uuid_val = self._mapper._map_uuid(user_id)
        uuid_str = str(uuid_val)
        stmt = select(TaskORM).where(
            TaskORM.assignee_ids.bool_op("@>")(type_coerce(uuid_str, JSONB))
        )
        result = await self._session.execute(stmt)
        return await self._to_domain_list_with_labels(result.scalars().all())

    async def get_by_reporter(self, user_id: Id) -> list[Task]:
        uuid_val = self._mapper._map_uuid(user_id)
        stmt = select(TaskORM).where(TaskORM.reporter_id == uuid_val)
        result = await self._session.execute(stmt)
        return await self._to_domain_list_with_labels(result.scalars().all())

    async def get_subtasks(self, parent_task_id: Id) -> list[Task]:
        uuid_val = self._mapper._map_uuid(parent_task_id)
        stmt = select(TaskORM).where(TaskORM.parent_task_id == uuid_val)
        result = await self._session.execute(stmt)
        return await self._to_domain_list_with_labels(result.scalars().all())

    async def get_by_sprint(self, sprint_id: Id) -> list[Task]:
        uuid_val = self._mapper._map_uuid(sprint_id)
        stmt = select(TaskORM).where(TaskORM.sprint_id == uuid_val)
        result = await self._session.execute(stmt)
        return await self._to_domain_list_with_labels(result.scalars().all())

    async def get_by_epic(self, epic_id: Id) -> list[Task]:
        uuid_val = self._mapper._map_uuid(epic_id)
        stmt = select(TaskORM).where(TaskORM.epic_id == uuid_val)
        result = await self._session.execute(stmt)
        return await self._to_domain_list_with_labels(result.scalars().all())

    async def get_overdue_tasks(self) -> list[Task]:
        today = date_type.today()
        stmt = select(TaskORM).where(
            and_(
                TaskORM.due_date < today,
                TaskORM.status == "active",
                TaskORM.completed_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return await self._to_domain_list_with_labels(result.scalars().all())

    async def get_by_status(self, project_id: Id, status_id: Id) -> list[Task]:
        project_uuid = self._mapper._map_uuid(project_id)
        status_uuid = self._mapper._map_uuid(status_id)
        stmt = select(TaskORM).where(
            and_(
                TaskORM.project_id == project_uuid,
                TaskORM.status_id == status_uuid,
            )
        )
        result = await self._session.execute(stmt)
        return await self._to_domain_list_with_labels(result.scalars().all())

    async def get_by_parent(self, parent_task_id: Id) -> list[Task]:
        return await self.get_subtasks(parent_task_id)

    async def get_by_labels(self, project_id: Id, label_names: list[str]) -> list[Task]:
        project_uuid = self._mapper._map_uuid(project_id)
        stmt = (
            select(TaskORM)
            .join(task_labels_table, task_labels_table.c.task_id == TaskORM.id)
            .where(
                and_(
                    TaskORM.project_id == project_uuid,
                    task_labels_table.c.label_name.in_(label_names),
                )
            )
            .distinct()
        )
        result = await self._session.execute(stmt)
        return await self._to_domain_list_with_labels(result.scalars().all())

    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[Task]:
        stmt = select(TaskORM)
        if filters:
            title = filters.get("title")
            if title:
                stmt = stmt.where(TaskORM.title.ilike(f"%{title}%"))
            status = filters.get("status")
            if status:
                stmt = stmt.where(TaskORM.status == status)
            project_id = filters.get("project_id")
            if project_id:
                stmt = stmt.where(TaskORM.project_id == project_id)
            task_type = filters.get("task_type")
            if task_type:
                stmt = stmt.where(TaskORM.task_type == task_type)
            priority = filters.get("priority")
            if priority:
                stmt = stmt.where(TaskORM.priority == priority)
        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return await self._to_domain_list_with_labels(result.scalars().all())

    async def count_by_project(self, project_id: Id) -> int:
        uuid_val = self._mapper._map_uuid(project_id)
        stmt = select(func.count()).select_from(TaskORM).where(TaskORM.project_id == uuid_val)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def count_by_status(self, project_id: Id, status_id: Id) -> int:
        project_uuid = self._mapper._map_uuid(project_id)
        status_uuid = self._mapper._map_uuid(status_id)
        stmt = select(func.count()).select_from(TaskORM).where(
            and_(
                TaskORM.project_id == project_uuid,
                TaskORM.status_id == status_uuid,
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def is_participant_in_project(self, project_id: Id, user_id: Id) -> bool:
        """Проверить, является ли пользователь участником задач проекта (assignee, reporter, watcher)."""
        project_uuid = self._mapper._map_uuid(project_id)
        user_uuid = self._mapper._map_uuid(user_id)
        user_uuid_str = str(user_uuid)

        # 1. Reporter
        stmt = select(func.count()).select_from(TaskORM).where(
            and_(
                TaskORM.project_id == project_uuid,
                TaskORM.reporter_id == user_uuid,
            )
        )
        result = await self._session.execute(stmt)
        if result.scalar_one() > 0:
            return True

        # 2. Assignee (JSONB contains)
        stmt = select(func.count()).select_from(TaskORM).where(
            and_(
                TaskORM.project_id == project_uuid,
                type_coerce(TaskORM.assignee_ids, JSONB).astext.contains(user_uuid_str),
            )
        )
        result = await self._session.execute(stmt)
        if result.scalar_one() > 0:
            return True

        # 3. Watcher
        stmt = (
            select(func.count())
            .select_from(TaskWatcherORM)
            .join(TaskORM, TaskWatcherORM.task_id == TaskORM.id)
            .where(
                and_(
                    TaskORM.project_id == project_uuid,
                    TaskWatcherORM.user_id == user_uuid,
                )
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one() > 0
