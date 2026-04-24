"""Интеграционные тесты UpdatePersonalInfoHandler (реальные repos + Kafka)."""

import pytest

from app.context.profile.application.commands.update_personal_info import (
    UpdatePersonalInfoCommand,
    UpdatePersonalInfoHandler,
)
from app.context.profile.domain.exceptions.profile_exceptions import ProfileNotFoundException
from app.context.profile.infrastructure.persistence.repositories.sql_user_profile_repository import (
    SqlUserProfileRepository,
)
from app.shared.application.messaging.broker_domain_event_bus import BrokerDomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.messaging.kafka_message_broker_adapter import KafkaMessageBrokerAdapter


@pytest.mark.integration
class TestUpdatePersonalInfoHandler:
    """Тесты обновления персональных данных — full stack."""

    @pytest.fixture
    def event_bus(self, kafka_producer) -> BrokerDomainEventBus:
        broker = KafkaMessageBrokerAdapter(producer=kafka_producer, bootstrap_servers="")
        return BrokerDomainEventBus(broker=broker, topic="profile.events.test")

    @pytest.fixture
    def handler(
        self,
        profile_repo: SqlUserProfileRepository,
        event_bus: BrokerDomainEventBus,
    ) -> UpdatePersonalInfoHandler:
        return UpdatePersonalInfoHandler(
            profile_repo=profile_repo,
            event_bus=event_bus,
        )

    async def test_update_bio_success(
        self, handler: UpdatePersonalInfoHandler, make_profile, profile_repo: SqlUserProfileRepository
    ) -> None:
        profile = await make_profile()

        cmd = UpdatePersonalInfoCommand(
            user_id=str(profile.user_id),
            bio="Senior Developer at TestCorp",
        )
        await handler.handle(cmd)

        updated = await profile_repo.get_by_user_id(profile.user_id)
        assert updated is not None
        assert updated.bio == "Senior Developer at TestCorp"

    async def test_update_job_title_success(
        self, handler: UpdatePersonalInfoHandler, make_profile, profile_repo: SqlUserProfileRepository
    ) -> None:
        profile = await make_profile()

        cmd = UpdatePersonalInfoCommand(
            user_id=str(profile.user_id),
            job_title="Tech Lead",
        )
        await handler.handle(cmd)

        updated = await profile_repo.get_by_user_id(profile.user_id)
        assert updated is not None
        assert updated.job_title == "Tech Lead"

    async def test_update_both_fields(
        self, handler: UpdatePersonalInfoHandler, make_profile, profile_repo: SqlUserProfileRepository
    ) -> None:
        profile = await make_profile()

        cmd = UpdatePersonalInfoCommand(
            user_id=str(profile.user_id),
            bio="About me",
            job_title="Engineer",
        )
        await handler.handle(cmd)

        updated = await profile_repo.get_by_user_id(profile.user_id)
        assert updated is not None
        assert updated.bio == "About me"
        assert updated.job_title == "Engineer"

    async def test_update_personal_info_profile_not_found(self, handler: UpdatePersonalInfoHandler) -> None:
        cmd = UpdatePersonalInfoCommand(
            user_id=str(Id.generate()),
            bio="Ghost user",
        )
        with pytest.raises(ProfileNotFoundException):
            await handler.handle(cmd)
