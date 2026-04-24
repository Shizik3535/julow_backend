"""Интеграционные тесты UpdateAppearanceHandler (реальные repos + Kafka)."""

import pytest

from app.context.profile.application.commands.update_appearance import (
    UpdateAppearanceCommand,
    UpdateAppearanceHandler,
)
from app.context.profile.domain.exceptions.profile_exceptions import ProfileNotFoundException
from app.context.profile.domain.value_objects.interface_density import InterfaceDensity
from app.context.profile.domain.value_objects.theme import Theme
from app.context.profile.infrastructure.persistence.repositories.sql_user_profile_repository import (
    SqlUserProfileRepository,
)
from app.shared.application.messaging.broker_domain_event_bus import BrokerDomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.messaging.kafka_message_broker_adapter import KafkaMessageBrokerAdapter


@pytest.mark.integration
class TestUpdateAppearanceHandler:
    """Тесты обновления настроек внешнего вида — full stack."""

    @pytest.fixture
    def event_bus(self, kafka_producer) -> BrokerDomainEventBus:
        broker = KafkaMessageBrokerAdapter(producer=kafka_producer, bootstrap_servers="")
        return BrokerDomainEventBus(broker=broker, topic="profile.events.test")

    @pytest.fixture
    def handler(
        self,
        profile_repo: SqlUserProfileRepository,
        event_bus: BrokerDomainEventBus,
    ) -> UpdateAppearanceHandler:
        return UpdateAppearanceHandler(
            profile_repo=profile_repo,
            event_bus=event_bus,
        )

    async def test_update_appearance_success(
        self, handler: UpdateAppearanceHandler, make_profile, profile_repo: SqlUserProfileRepository
    ) -> None:
        profile = await make_profile()

        cmd = UpdateAppearanceCommand(
            user_id=str(profile.user_id),
            theme="dark",
            accent_color="#FF5733",
            interface_density="compact",
        )
        await handler.handle(cmd)

        updated = await profile_repo.get_by_user_id(profile.user_id)
        assert updated is not None
        assert updated.appearance.theme == Theme.DARK
        assert updated.appearance.interface_density == InterfaceDensity.COMPACT

    async def test_update_appearance_profile_not_found(self, handler: UpdateAppearanceHandler) -> None:
        cmd = UpdateAppearanceCommand(
            user_id=str(Id.generate()),
            theme="light",
        )
        with pytest.raises(ProfileNotFoundException):
            await handler.handle(cmd)
