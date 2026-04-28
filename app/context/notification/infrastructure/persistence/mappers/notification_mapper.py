from __future__ import annotations

from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.notification.domain.aggregates.notification import Notification
from app.context.notification.domain.value_objects.channel_type import ChannelType
from app.context.notification.domain.value_objects.notification_group_key import NotificationGroupKey
from app.context.notification.domain.value_objects.notification_priority import NotificationPriority
from app.context.notification.domain.value_objects.notification_type import NotificationType
from app.context.notification.infrastructure.persistence.orm_models.notification_orm import NotificationORM


class NotificationMapper(BaseMapper[Notification, NotificationORM]):
    """Data Mapper: Notification ↔ NotificationORM."""

    def to_domain(self, orm_model: NotificationORM) -> Notification:
        # NotificationGroupKey (скаляры → VO)
        group_key = None
        if orm_model.group_key_type is not None:
            target_id = (
                self._map_id(orm_model.group_key_target_id)
                if orm_model.group_key_target_id
                else None
            )
            group_key = NotificationGroupKey(
                type=NotificationType(orm_model.group_key_type),
                target_id=target_id,
                window_minutes=orm_model.group_key_window_minutes or 5,
            )

        # channels (JSON → list[ChannelType])
        channels = []
        if orm_model.channels:
            channels = [ChannelType(ch) for ch in orm_model.channels]

        return Notification(
            id=self._map_id(orm_model.id),
            recipient_id=self._map_id(orm_model.recipient_id),
            workspace_id=self._map_id(orm_model.workspace_id) if orm_model.workspace_id else None,
            notification_type=NotificationType(orm_model.notification_type),
            title=orm_model.title,
            body=orm_model.body,
            priority=NotificationPriority(orm_model.priority),
            data=orm_model.data or {},
            channels=channels,
            is_read=orm_model.is_read,
            read_at=orm_model.read_at,
            is_archived=orm_model.is_archived,
            group_key=group_key,
            actor_id=self._map_id(orm_model.actor_id) if orm_model.actor_id else None,
            created_at=orm_model.created_at,
        )

    def to_orm(self, aggregate: Notification) -> NotificationORM:
        # NotificationGroupKey (VO → скаляры)
        gk = aggregate.group_key
        group_key_type = gk.type.value if gk else None
        group_key_target_id = self._map_uuid(gk.target_id) if gk and gk.target_id else None
        group_key_window_minutes = gk.window_minutes if gk else None

        # channels (list[ChannelType] → JSON)
        channels = [ch.value for ch in aggregate.channels] if aggregate.channels else None

        return NotificationORM(
            id=self._map_uuid(aggregate.id),
            recipient_id=self._map_uuid(aggregate.recipient_id),
            workspace_id=self._map_uuid(aggregate.workspace_id) if aggregate.workspace_id else None,
            notification_type=aggregate.notification_type.value,
            title=aggregate.title,
            body=aggregate.body,
            priority=aggregate.priority.value,
            data=aggregate.data if aggregate.data else None,
            channels=channels,
            is_read=aggregate.is_read,
            read_at=aggregate.read_at,
            is_archived=aggregate.is_archived,
            group_key_type=group_key_type,
            group_key_target_id=group_key_target_id,
            group_key_window_minutes=group_key_window_minutes,
            actor_id=self._map_uuid(aggregate.actor_id) if aggregate.actor_id else None,
            created_at=aggregate.created_at,
        )
