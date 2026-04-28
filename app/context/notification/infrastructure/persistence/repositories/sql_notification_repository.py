from __future__ import annotations

from sqlalchemy import and_, func, select, update
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.notification.domain.aggregates.notification import Notification
from app.context.notification.domain.repositories.notification_repository import NotificationRepository
from app.context.notification.domain.value_objects.notification_group_key import NotificationGroupKey
from app.context.notification.domain.value_objects.notification_type import NotificationType
from app.context.notification.infrastructure.persistence.mappers.notification_mapper import NotificationMapper
from app.context.notification.infrastructure.persistence.orm_models.notification_orm import NotificationORM


class SqlNotificationRepository(
    SqlAlchemyRepository[Notification, NotificationORM],
    NotificationRepository,
):
    """SQLAlchemy-реализация NotificationRepository."""

    def __init__(self, session: AsyncSession, mapper: NotificationMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=NotificationORM)

    async def get_unread_by_user(self, user_id: Id) -> list[Notification]:
        uuid_val = self._mapper._map_uuid(user_id)
        stmt = (
            select(NotificationORM)
            .where(NotificationORM.recipient_id == uuid_val, NotificationORM.is_read == False)
            .order_by(NotificationORM.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_by_user(self, user_id: Id) -> list[Notification]:
        uuid_val = self._mapper._map_uuid(user_id)
        stmt = (
            select(NotificationORM)
            .where(NotificationORM.recipient_id == uuid_val)
            .order_by(NotificationORM.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_by_user_and_workspace(self, user_id: Id, workspace_id: Id) -> list[Notification]:
        user_uuid = self._mapper._map_uuid(user_id)
        ws_uuid = self._mapper._map_uuid(workspace_id)
        stmt = (
            select(NotificationORM)
            .where(
                NotificationORM.recipient_id == user_uuid,
                NotificationORM.workspace_id == ws_uuid,
            )
            .order_by(NotificationORM.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def count_unread(self, user_id: Id) -> int:
        uuid_val = self._mapper._map_uuid(user_id)
        stmt = (
            select(func.count())
            .select_from(NotificationORM)
            .where(NotificationORM.recipient_id == uuid_val, NotificationORM.is_read == False)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def count_unread_by_workspace(self, user_id: Id, workspace_id: Id) -> int:
        user_uuid = self._mapper._map_uuid(user_id)
        ws_uuid = self._mapper._map_uuid(workspace_id)
        stmt = (
            select(func.count())
            .select_from(NotificationORM)
            .where(
                NotificationORM.recipient_id == user_uuid,
                NotificationORM.workspace_id == ws_uuid,
                NotificationORM.is_read == False,
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def mark_all_read(self, user_id: Id, workspace_id: Id | None = None) -> int:
        from datetime import datetime, timezone

        uuid_val = self._mapper._map_uuid(user_id)
        conditions = [NotificationORM.recipient_id == uuid_val, NotificationORM.is_read == False]
        if workspace_id is not None:
            ws_uuid = self._mapper._map_uuid(workspace_id)
            conditions.append(NotificationORM.workspace_id == ws_uuid)
        stmt = (
            update(NotificationORM)
            .where(*conditions)
            .values(is_read=True, read_at=datetime.now(tz=timezone.utc))
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount

    async def get_by_group_key(self, group_key: NotificationGroupKey, recipient_id: Id | None = None) -> list[Notification]:
        stmt = (
            select(NotificationORM)
            .where(
                NotificationORM.group_key_type == group_key.type.value,
                NotificationORM.group_key_window_minutes == group_key.window_minutes,
            )
        )
        if recipient_id is not None:
            recipient_uuid = self._mapper._map_uuid(recipient_id)
            stmt = stmt.where(NotificationORM.recipient_id == recipient_uuid)
        if group_key.target_id:
            target_uuid = self._mapper._map_uuid(group_key.target_id)
            stmt = stmt.where(NotificationORM.group_key_target_id == target_uuid)
        else:
            stmt = stmt.where(NotificationORM.group_key_target_id.is_(None))

        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_archived(self, user_id: Id) -> list[Notification]:
        uuid_val = self._mapper._map_uuid(user_id)
        stmt = (
            select(NotificationORM)
            .where(NotificationORM.recipient_id == uuid_val, NotificationORM.is_archived == True)
            .order_by(NotificationORM.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def has_unread_by_type_and_target(
        self,
        recipient_id: Id,
        notification_type: NotificationType,
        target_key: str,
    ) -> bool:
        """Проверить наличие unread уведомления данного типа для target_key в data.

        Note: Использует PostgreSQL-специфичный JSONB-запрос (data["key"].as_string()).
        Для SQLite или других СУБД потребуется другая реализация.
        """
        from sqlalchemy import or_

        recipient_uuid = self._mapper._map_uuid(recipient_id)
        stmt = (
            select(func.count())
            .select_from(NotificationORM)
            .where(
                and_(
                    NotificationORM.recipient_id == recipient_uuid,
                    NotificationORM.notification_type == notification_type.value,
                    NotificationORM.is_read == False,
                    or_(
                        NotificationORM.data["task_id"].as_string() == target_key,
                        NotificationORM.data["project_id"].as_string() == target_key,
                    ),
                )
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one() > 0
