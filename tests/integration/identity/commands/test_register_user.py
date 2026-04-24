"""Интеграционные тесты RegisterUserHandler (реальные repos + реальные порты)."""

import pytest

from app.context.identity.application.commands.register_user import (
    RegisterUserCommand,
    RegisterUserHandler,
)
from app.context.identity.application.exceptions.user_app_exceptions import (
    UserAlreadyExistsException,
)
from app.context.identity.domain.value_objects.account_status import AccountStatus
from app.context.identity.infrastructure.persistence.repositories.sql_role_repository import SqlRoleRepository
from app.context.identity.infrastructure.persistence.repositories.sql_user_auth_repository import (
    SqlUserAuthRepository,
)
from app.context.identity.infrastructure.persistence.repositories.sql_user_repository import SqlUserRepository
from app.shared.application.messaging.broker_domain_event_bus import BrokerDomainEventBus
from app.shared.application.ports.auth.password_port import PasswordPort
from app.shared.infrastructure.messaging.kafka_message_broker_adapter import KafkaMessageBrokerAdapter
from app.shared.infrastructure.notification.smtp_email_adapter import SmtpEmailAdapter
from app.context.identity.infrastructure.notification.identity_notification_adapter import (
    IdentityNotificationAdapter,
)
from app.context.identity.application.ports.notification.identity_notification_port import (
    IdentityNotificationPort,
)
from app.shared.domain.value_objects.email_vo import Email


@pytest.mark.integration
class TestRegisterUserHandler:
    """Тесты регистрации пользователя — full stack."""

    @pytest.fixture
    def notification_adapter(self, smtp_host, smtp_port) -> IdentityNotificationPort:
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
        user_repo: SqlUserRepository,
        user_auth_repo: SqlUserAuthRepository,
        role_repo: SqlRoleRepository,
        password_adapter: PasswordPort,
        event_bus: BrokerDomainEventBus,
        notification_adapter: IdentityNotificationPort,
    ) -> RegisterUserHandler:
        return RegisterUserHandler(
            user_repo=user_repo,
            user_auth_repo=user_auth_repo,
            role_repo=role_repo,
            password_port=password_adapter,
            event_bus=event_bus,
            notification_port=notification_adapter,
        )

    async def test_register_user_success(
        self, handler: RegisterUserHandler, user_repo, make_role
    ) -> None:
        # Создаём дефолтную роль "user"
        await make_role(name="user", is_system=True)

        cmd = RegisterUserCommand(
            email="newuser@test.com",
            password="StrongPass123!",
            auth_provider="email_password",
        )
        result = await handler.handle(cmd)
        assert result is not None

        # Проверяем, что User записан в БД
        user = await user_repo.get_by_email(Email("newuser@test.com"))
        assert user is not None
        assert user.status == AccountStatus.PENDING_VERIFICATION

    async def test_register_duplicate_email_raises(
        self, handler: RegisterUserHandler, make_role, make_user
    ) -> None:
        await make_role(name="user", is_system=True)
        existing = await make_user(email="duplicate@test.com")

        cmd = RegisterUserCommand(
            email="duplicate@test.com",
            password="StrongPass123!",
            auth_provider="email_password",
        )
        with pytest.raises(UserAlreadyExistsException):
            await handler.handle(cmd)
