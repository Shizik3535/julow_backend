"""Интеграционные тесты ConfirmEmailHandler (реальные repos + Kafka)."""

from datetime import datetime, timedelta, timezone

import pytest

from app.context.identity.application.commands.confirm_email import (
    ConfirmEmailCommand,
    ConfirmEmailHandler,
)
from app.context.identity.domain.value_objects.account_status import AccountStatus
from app.context.identity.domain.value_objects.verification_token import VerificationToken
from app.context.identity.domain.value_objects.verification_type import VerificationType
from app.context.identity.infrastructure.persistence.repositories.sql_user_auth_repository import (
    SqlUserAuthRepository,
)
from app.context.identity.infrastructure.persistence.repositories.sql_user_repository import SqlUserRepository
from app.shared.application.messaging.broker_domain_event_bus import BrokerDomainEventBus
from app.shared.infrastructure.messaging.kafka_message_broker_adapter import KafkaMessageBrokerAdapter


@pytest.mark.integration
class TestConfirmEmailHandler:
    """Тесты подтверждения email — full stack."""

    @pytest.fixture
    def event_bus(self, kafka_producer) -> BrokerDomainEventBus:
        broker = KafkaMessageBrokerAdapter(producer=kafka_producer, bootstrap_servers="")
        return BrokerDomainEventBus(broker=broker, topic="identity.events.test")

    @pytest.fixture
    def handler(
        self,
        user_repo: SqlUserRepository,
        user_auth_repo: SqlUserAuthRepository,
        event_bus: BrokerDomainEventBus,
    ) -> ConfirmEmailHandler:
        return ConfirmEmailHandler(
            user_repo=user_repo,
            user_auth_repo=user_auth_repo,
            event_bus=event_bus,
        )

    async def test_confirm_email_success(
        self,
        handler: ConfirmEmailHandler,
        make_user,
        make_user_auth,
        user_repo: SqlUserRepository,
        user_auth_repo: SqlUserAuthRepository,
    ) -> None:
        user = await make_user(email="confirm@test.com")
        auth = await make_user_auth(user_id=user.id, email="confirm@test.com")

        # Добавляем verification token
        expires = datetime.now(tz=timezone.utc) + timedelta(hours=24)
        token = VerificationToken(
            value="confirm-token-123",
            token_type=VerificationType.EMAIL_CONFIRMATION,
            expires_at=expires,
        )
        auth.request_email_verification(token=token, expires_at=expires)
        await user_auth_repo.update(auth)

        cmd = ConfirmEmailCommand(user_id=str(user.id), token="confirm-token-123")
        await handler.handle(cmd)

        # Проверяем, что User стал ACTIVE
        updated_user = await user_repo.get_by_id(user.id)
        assert updated_user is not None
        assert updated_user.status == AccountStatus.ACTIVE
        assert updated_user.is_email_confirmed is True
