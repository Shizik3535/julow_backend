"""Интеграционные тесты UpdateNotificationsHandler (реальные repos + Kafka)."""

import pytest

from app.context.profile.application.commands.update_notifications import (
    TypePreferenceInput,
    UpdateNotificationsCommand,
    UpdateNotificationsHandler,
)
from app.context.profile.domain.exceptions.profile_exceptions import ProfileNotFoundException
from app.context.profile.domain.value_objects.notification_channel import NotificationChannel
from app.context.profile.domain.value_objects.notification_type import NotificationType
from app.context.profile.infrastructure.persistence.repositories.sql_user_profile_repository import (
    SqlUserProfileRepository,
)
from app.shared.application.messaging.broker_domain_event_bus import BrokerDomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.messaging.kafka_message_broker_adapter import KafkaMessageBrokerAdapter


@pytest.mark.integration
class TestUpdateNotificationsHandler:
    """Тесты обновления настроек уведомлений — full stack."""

    @pytest.fixture
    def event_bus(self, kafka_producer) -> BrokerDomainEventBus:
        broker = KafkaMessageBrokerAdapter(producer=kafka_producer, bootstrap_servers="")
        return BrokerDomainEventBus(broker=broker, topic="profile.events.test")

    @pytest.fixture
    def handler(
        self,
        profile_repo: SqlUserProfileRepository,
        event_bus: BrokerDomainEventBus,
    ) -> UpdateNotificationsHandler:
        return UpdateNotificationsHandler(
            profile_repo=profile_repo,
            event_bus=event_bus,
        )

    async def test_update_notifications_success(
        self, handler: UpdateNotificationsHandler, make_profile, profile_repo: SqlUserProfileRepository
    ) -> None:
        profile = await make_profile()

        cmd = UpdateNotificationsCommand(
            user_id=str(profile.user_id),
            type_preferences=[
                TypePreferenceInput(
                    notification_type="task_assigned",
                    is_enabled=True,
                    channels={"in_app": True, "email": True, "push": False, "sms": False},
                ),
                TypePreferenceInput(
                    notification_type="mention",
                    is_enabled=True,
                    channels={"in_app": True, "email": False, "push": True, "sms": False},
                ),
            ],
        )
        await handler.handle(cmd)

        updated = await profile_repo.get_by_user_id(profile.user_id)
        assert updated is not None
        assert len(updated.notifications.type_preferences) == 2
        tp_task = next(
            tp for tp in updated.notifications.type_preferences
            if tp.notification_type == NotificationType.TASK_ASSIGNED
        )
        assert tp_task.is_enabled is True

    async def test_update_notifications_disable_type(
        self, handler: UpdateNotificationsHandler, make_profile, profile_repo: SqlUserProfileRepository
    ) -> None:
        profile = await make_profile()

        cmd = UpdateNotificationsCommand(
            user_id=str(profile.user_id),
            type_preferences=[
                TypePreferenceInput(
                    notification_type="system_announcement",
                    is_enabled=False,
                    channels={"in_app": False, "email": False, "push": False, "sms": False},
                ),
            ],
        )
        await handler.handle(cmd)

        updated = await profile_repo.get_by_user_id(profile.user_id)
        assert updated is not None
        tp_sys = next(
            tp for tp in updated.notifications.type_preferences
            if tp.notification_type == NotificationType.SYSTEM_ANNOUNCEMENT
        )
        assert tp_sys.is_enabled is False

    async def test_update_notifications_profile_not_found(self, handler: UpdateNotificationsHandler) -> None:
        cmd = UpdateNotificationsCommand(
            user_id=str(Id.generate()),
            type_preferences=[
                TypePreferenceInput(
                    notification_type="task_assigned",
                    is_enabled=True,
                    channels={"in_app": True},
                ),
            ],
        )
        with pytest.raises(ProfileNotFoundException):
            await handler.handle(cmd)
