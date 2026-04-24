"""Интеграционные тесты UpdatePrivacyHandler (реальные repos + Kafka)."""

import pytest

from app.context.profile.application.commands.update_privacy import (
    UpdatePrivacyCommand,
    UpdatePrivacyHandler,
)
from app.context.profile.domain.exceptions.profile_exceptions import ProfileNotFoundException
from app.context.profile.domain.value_objects.activity_tracking_consent import ActivityTrackingConsent
from app.context.profile.domain.value_objects.online_status_visibility import OnlineStatusVisibility
from app.context.profile.domain.value_objects.profile_visibility import ProfileVisibility
from app.context.profile.infrastructure.persistence.repositories.sql_user_profile_repository import (
    SqlUserProfileRepository,
)
from app.shared.application.messaging.broker_domain_event_bus import BrokerDomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.messaging.kafka_message_broker_adapter import KafkaMessageBrokerAdapter


@pytest.mark.integration
class TestUpdatePrivacyHandler:
    """Тесты обновления настроек приватности — full stack."""

    @pytest.fixture
    def event_bus(self, kafka_producer) -> BrokerDomainEventBus:
        broker = KafkaMessageBrokerAdapter(producer=kafka_producer, bootstrap_servers="")
        return BrokerDomainEventBus(broker=broker, topic="profile.events.test")

    @pytest.fixture
    def handler(
        self,
        profile_repo: SqlUserProfileRepository,
        event_bus: BrokerDomainEventBus,
    ) -> UpdatePrivacyHandler:
        return UpdatePrivacyHandler(
            profile_repo=profile_repo,
            event_bus=event_bus,
        )

    async def test_update_privacy_success(
        self, handler: UpdatePrivacyHandler, make_profile, profile_repo: SqlUserProfileRepository
    ) -> None:
        profile = await make_profile()

        cmd = UpdatePrivacyCommand(
            user_id=str(profile.user_id),
            profile_visibility="private",
            online_status_visibility="nobody",
            activity_tracking_consent="denied",
        )
        await handler.handle(cmd)

        updated = await profile_repo.get_by_user_id(profile.user_id)
        assert updated is not None
        assert updated.privacy.profile_visibility == ProfileVisibility.PRIVATE
        assert updated.privacy.online_status_visibility == OnlineStatusVisibility.NOBODY
        assert updated.privacy.activity_tracking_consent == ActivityTrackingConsent.DENIED

    async def test_update_privacy_partial_change(
        self, handler: UpdatePrivacyHandler, make_profile, profile_repo: SqlUserProfileRepository
    ) -> None:
        profile = await make_profile()

        cmd = UpdatePrivacyCommand(
            user_id=str(profile.user_id),
            profile_visibility="public",
            online_status_visibility="contacts_only",
            activity_tracking_consent="granted",
        )
        await handler.handle(cmd)

        updated = await profile_repo.get_by_user_id(profile.user_id)
        assert updated is not None
        assert updated.privacy.profile_visibility == ProfileVisibility.PUBLIC
        assert updated.privacy.online_status_visibility == OnlineStatusVisibility.CONTACTS_ONLY
        assert updated.privacy.activity_tracking_consent == ActivityTrackingConsent.GRANTED

    async def test_update_privacy_profile_not_found(self, handler: UpdatePrivacyHandler) -> None:
        cmd = UpdatePrivacyCommand(
            user_id=str(Id.generate()),
            profile_visibility="public",
        )
        with pytest.raises(ProfileNotFoundException):
            await handler.handle(cmd)
