from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.notification.domain.aggregates.notification_preferences import NotificationPreferences
from app.context.notification.domain.entities.digest_config import DigestConfig
from app.context.notification.domain.entities.do_not_disturb_schedule import DoNotDisturbSchedule
from app.context.notification.domain.entities.preference_entry import PreferenceEntry
from app.context.notification.domain.value_objects.channel_type import ChannelType
from app.context.notification.domain.value_objects.digest_frequency import DigestFrequency
from app.context.notification.domain.value_objects.notification_policy import NotificationPolicy
from app.context.notification.domain.value_objects.notification_type import NotificationType
from app.context.notification.domain.value_objects.preference_scope import PreferenceScope
from app.context.notification.infrastructure.persistence.orm_models.notification_preferences_orm import (
    NotificationPreferencesORM,
    PreferenceEntryORM,
)


class NotificationPreferencesMapper(BaseMapper[NotificationPreferences, NotificationPreferencesORM]):
    """Data Mapper: NotificationPreferences ↔ NotificationPreferencesORM."""

    def to_domain(self, orm_model: NotificationPreferencesORM) -> NotificationPreferences:
        # NotificationPolicy (JSON → VO)
        mandatory_types = frozenset()
        if orm_model.policy_mandatory_types:
            mandatory_types = frozenset(
                NotificationType(t) for t in orm_model.policy_mandatory_types
            )

        default_channels = {}
        if orm_model.policy_default_channels:
            for type_val, channels_list in orm_model.policy_default_channels.items():
                default_channels[NotificationType(type_val)] = [
                    ChannelType(ch) for ch in channels_list
                ]

        policy = NotificationPolicy(
            mandatory_types=mandatory_types,
            default_channels=default_channels,
        )

        # DoNotDisturbSchedule (скаляры → entity)
        dnd = None
        if orm_model.dnd_enabled or orm_model.dnd_start is not None:
            dnd = DoNotDisturbSchedule(
                enabled=orm_model.dnd_enabled,
                schedule_start=orm_model.dnd_start,
                schedule_end=orm_model.dnd_end,
                schedule_days=orm_model.dnd_days,
                timezone=orm_model.dnd_timezone,
            )

        # DigestConfig (скаляры → entity)
        digest = None
        if orm_model.digest_enabled or orm_model.digest_time is not None:
            digest = DigestConfig(
                is_enabled=orm_model.digest_enabled,
                frequency=DigestFrequency(orm_model.digest_frequency),
                delivery_time=orm_model.digest_time,
                delivery_day=orm_model.digest_day,
                timezone=orm_model.digest_timezone,
            )

        # PreferenceEntry (relationship → entities)
        preferences = [
            self._entry_orm_to_domain(entry_orm)
            for entry_orm in orm_model.preference_entries
        ]

        return NotificationPreferences(
            id=self._map_id(orm_model.id),
            user_id=self._map_id(orm_model.user_id),
            preferences=preferences,
            dnd_schedule=dnd,
            digest_config=digest,
            policy=policy,
            reminder_window_hours=orm_model.reminder_window_hours,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
            _skip_defaults=True,
        )

    def to_orm(self, aggregate: NotificationPreferences) -> NotificationPreferencesORM:
        # NotificationPolicy (VO → JSON)
        policy = aggregate.policy
        mandatory_types = [t.value for t in policy.mandatory_types] if policy.mandatory_types else None
        default_channels = None
        if policy.default_channels:
            default_channels = {
                t.value: [ch.value for ch in channels]
                for t, channels in policy.default_channels.items()
            }

        # DoNotDisturbSchedule (entity → скаляры)
        dnd = aggregate.dnd_schedule
        dnd_enabled = dnd.enabled if dnd else False
        dnd_start = dnd.schedule_start if dnd else None
        dnd_end = dnd.schedule_end if dnd else None
        dnd_days = dnd.schedule_days if dnd else None
        dnd_timezone = dnd.timezone if dnd else "UTC"

        # DigestConfig (entity → скаляры)
        digest = aggregate.digest_config
        digest_enabled = digest.is_enabled if digest else False
        digest_frequency = digest.frequency.value if digest else "daily"
        digest_time = digest.delivery_time if digest else None
        digest_day = digest.delivery_day if digest else None
        digest_timezone = digest.timezone if digest else "UTC"

        orm = NotificationPreferencesORM(
            id=self._map_uuid(aggregate.id),
            user_id=self._map_uuid(aggregate.user_id),
            policy_mandatory_types=mandatory_types,
            policy_default_channels=default_channels,
            dnd_enabled=dnd_enabled,
            dnd_start=dnd_start,
            dnd_end=dnd_end,
            dnd_days=dnd_days,
            dnd_timezone=dnd_timezone,
            digest_enabled=digest_enabled,
            digest_frequency=digest_frequency,
            digest_time=digest_time,
            digest_day=digest_day,
            digest_timezone=digest_timezone,
            reminder_window_hours=aggregate.reminder_window_hours,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )

        # PreferenceEntry (entities → relationship)
        orm.preference_entries = [
            self._entry_to_orm(entry, aggregate.id)
            for entry in aggregate.preferences
        ]

        return orm

    def _entry_orm_to_domain(self, orm: PreferenceEntryORM) -> PreferenceEntry:
        """Преобразовать PreferenceEntryORM → PreferenceEntry."""
        return PreferenceEntry(
            id=self._map_id(orm.id),
            notification_type=NotificationType(orm.notification_type),
            channel=ChannelType(orm.channel),
            enabled=orm.enabled,
            scope=PreferenceScope(orm.scope),
            scope_id=self._map_id(orm.scope_id) if orm.scope_id else None,
        )

    def _entry_to_orm(self, entry: PreferenceEntry, preferences_id: Id) -> PreferenceEntryORM:
        """Преобразовать PreferenceEntry → PreferenceEntryORM."""
        return PreferenceEntryORM(
            id=self._map_uuid(entry.id),
            preferences_id=self._map_uuid(preferences_id),
            notification_type=entry.notification_type.value,
            channel=entry.channel.value,
            enabled=entry.enabled,
            scope=entry.scope.value,
            scope_id=self._map_uuid(entry.scope_id) if entry.scope_id else None,
        )
