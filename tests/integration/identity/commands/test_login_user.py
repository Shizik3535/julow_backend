"""Интеграционные тесты LoginUserHandler (реальные repos + реальные порты)."""

import pytest

from app.context.identity.application.commands.login_user import LoginUserCommand, LoginUserHandler
from app.context.identity.application.exceptions.auth_app_exceptions import AuthenticationFailedException
from app.context.identity.domain.value_objects.failed_login_policy import FailedLoginPolicy
from app.context.identity.domain.value_objects.lockout_threshold import LockoutThreshold
from app.context.identity.domain.value_objects.password_hash import PasswordHash
from app.context.identity.infrastructure.persistence.repositories.sql_session_repository import SqlSessionRepository
from app.context.identity.infrastructure.persistence.repositories.sql_user_auth_repository import (
    SqlUserAuthRepository,
)
from app.context.identity.infrastructure.persistence.repositories.sql_user_repository import SqlUserRepository
from app.shared.application.messaging.broker_domain_event_bus import BrokerDomainEventBus
from app.shared.application.ports.auth.auth_port import AuthTokenPort
from app.shared.application.ports.auth.password_port import PasswordPort
from app.shared.infrastructure.messaging.kafka_message_broker_adapter import KafkaMessageBrokerAdapter
from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id


@pytest.mark.integration
class TestLoginUserHandler:
    """Тесты входа пользователя — full stack."""

    @pytest.fixture
    def event_bus(self, kafka_producer) -> BrokerDomainEventBus:
        broker = KafkaMessageBrokerAdapter(producer=kafka_producer, bootstrap_servers="")
        return BrokerDomainEventBus(broker=broker, topic="identity.events.test")

    @pytest.fixture
    def login_policy(self) -> FailedLoginPolicy:
        return FailedLoginPolicy(thresholds=[
            LockoutThreshold(failed_attempts=3, lock_duration_minutes=15),
        ])

    @pytest.fixture
    def handler(
        self,
        user_repo: SqlUserRepository,
        user_auth_repo: SqlUserAuthRepository,
        session_repo: SqlSessionRepository,
        password_adapter: PasswordPort,
        jwt_adapter: AuthTokenPort,
        login_policy: FailedLoginPolicy,
        event_bus: BrokerDomainEventBus,
    ) -> LoginUserHandler:
        return LoginUserHandler(
            user_repo=user_repo,
            user_auth_repo=user_auth_repo,
            session_repo=session_repo,
            password_port=password_adapter,
            auth_token_port=jwt_adapter,
            failed_login_policy=login_policy,
            event_bus=event_bus,
        )

    async def test_login_success(
        self,
        handler: LoginUserHandler,
        make_user,
        make_user_auth,
        password_adapter: PasswordPort,
        session_repo: SqlSessionRepository,
    ) -> None:
        user = await make_user(email="login@test.com")
        user.confirm_email()
        user.clear_domain_events()

        hashed = password_adapter.hash_password("CorrectPass123!")
        await make_user_auth(user_id=user.id, email="login@test.com", password_hash=hashed)

        cmd = LoginUserCommand(
            email="login@test.com",
            password="CorrectPass123!",
            ip="10.0.0.1",
            user_agent="TestBrowser",
        )
        result = await handler.handle(cmd)
        assert result is not None
        assert result.access_token
        assert result.refresh_token

    async def test_login_wrong_password(
        self,
        handler: LoginUserHandler,
        make_user,
        make_user_auth,
        password_adapter: PasswordPort,
    ) -> None:
        user = await make_user(email="wrongpw@test.com")
        user.confirm_email()
        user.clear_domain_events()

        hashed = password_adapter.hash_password("RightPassword!")
        await make_user_auth(user_id=user.id, email="wrongpw@test.com", password_hash=hashed)

        cmd = LoginUserCommand(
            email="wrongpw@test.com",
            password="WrongPassword!",
            ip="10.0.0.1",
            user_agent="TestBrowser",
        )
        with pytest.raises(AuthenticationFailedException):
            await handler.handle(cmd)
