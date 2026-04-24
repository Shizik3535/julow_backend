"""Интеграционные тесты ChangePasswordHandler (реальные repos + реальные порты)."""

import pytest

from app.context.identity.application.commands.change_password import (
    ChangePasswordCommand,
    ChangePasswordHandler,
)
from app.context.identity.application.exceptions.auth_app_exceptions import AuthenticationFailedException
from app.context.identity.infrastructure.persistence.repositories.sql_user_auth_repository import (
    SqlUserAuthRepository,
)
from app.shared.application.messaging.broker_domain_event_bus import BrokerDomainEventBus
from app.shared.application.ports.auth.password_port import PasswordPort
from app.shared.infrastructure.messaging.kafka_message_broker_adapter import KafkaMessageBrokerAdapter
from app.shared.infrastructure.notification.smtp_email_adapter import SmtpEmailAdapter
from app.context.identity.infrastructure.notification.identity_notification_adapter import (
    IdentityNotificationAdapter,
)


@pytest.mark.integration
class TestChangePasswordHandler:
    """Тесты смены пароля — full stack."""

    @pytest.fixture
    def notification_adapter(self, smtp_host, smtp_port):
        email_port = SmtpEmailAdapter(
            host=smtp_host, port=smtp_port, username=None, password=None, use_tls=False,
        )
        return IdentityNotificationAdapter(email_port=email_port, frontend_base_url="http://localhost:3000")

    @pytest.fixture
    def event_bus(self, kafka_producer) -> BrokerDomainEventBus:
        broker = KafkaMessageBrokerAdapter(producer=kafka_producer, bootstrap_servers="")
        return BrokerDomainEventBus(broker=broker, topic="identity.events.test")

    @pytest.fixture
    def handler(
        self,
        user_auth_repo: SqlUserAuthRepository,
        password_adapter: PasswordPort,
        event_bus: BrokerDomainEventBus,
        notification_adapter,
    ) -> ChangePasswordHandler:
        return ChangePasswordHandler(
            user_auth_repo=user_auth_repo,
            password_port=password_adapter,
            event_bus=event_bus,
            notification_port=notification_adapter,
        )

    async def test_change_password_success(
        self,
        handler: ChangePasswordHandler,
        make_user_auth,
        user_auth_repo: SqlUserAuthRepository,
        password_adapter: PasswordPort,
    ) -> None:
        old_hash = password_adapter.hash_password("OldPassword123!")
        auth = await make_user_auth(password_hash=old_hash)

        cmd = ChangePasswordCommand(
            user_id=str(auth.user_id),
            current_password="OldPassword123!",
            new_password="NewPassword456!",
        )
        await handler.handle(cmd)

        # Проверяем, что пароль обновился в БД
        updated = await user_auth_repo.get_by_id(auth.id)
        assert updated is not None
        assert password_adapter.verify_password("NewPassword456!", updated.password_hash.value) is True
        assert password_adapter.verify_password("OldPassword123!", updated.password_hash.value) is False

    async def test_change_password_wrong_current(
        self,
        handler: ChangePasswordHandler,
        make_user_auth,
        password_adapter: PasswordPort,
    ) -> None:
        old_hash = password_adapter.hash_password("CorrectOld!")
        auth = await make_user_auth(password_hash=old_hash)

        cmd = ChangePasswordCommand(
            user_id=str(auth.user_id),
            current_password="WrongOld!",
            new_password="NewPassword456!",
        )
        with pytest.raises(AuthenticationFailedException):
            await handler.handle(cmd)
