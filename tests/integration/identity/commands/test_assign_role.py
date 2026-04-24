"""Интеграционные тесты AssignRoleHandler (реальные repos + Kafka)."""

import pytest

from app.context.identity.application.commands.assign_role import AssignRoleCommand, AssignRoleHandler
from app.context.identity.application.ports.authorization.permission_checker_port import PermissionCheckerPort
from app.context.identity.domain.exceptions.user_exceptions import DuplicateRoleException
from app.context.identity.infrastructure.persistence.repositories.sql_role_repository import SqlRoleRepository
from app.context.identity.infrastructure.persistence.repositories.sql_user_repository import SqlUserRepository
from app.shared.application.messaging.broker_domain_event_bus import BrokerDomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.messaging.kafka_message_broker_adapter import KafkaMessageBrokerAdapter


@pytest.mark.integration
class TestAssignRoleHandler:
    """Тесты назначения роли — full stack."""

    @pytest.fixture
    def event_bus(self, kafka_producer) -> BrokerDomainEventBus:
        broker = KafkaMessageBrokerAdapter(producer=kafka_producer, bootstrap_servers="")
        return BrokerDomainEventBus(broker=broker, topic="identity.events.test")

    @pytest.fixture
    def permission_checker(self) -> PermissionCheckerPort:
        """Стаб: всегда разрешает."""

        class _AlwaysAllow(PermissionCheckerPort):
            async def has_permission(self, user_id: Id, permission: str) -> bool:
                return True

            async def require_permission(self, user_id: Id, permission: str) -> None:
                pass

        return _AlwaysAllow()

    @pytest.fixture
    def handler(
        self,
        user_repo: SqlUserRepository,
        role_repo: SqlRoleRepository,
        event_bus: BrokerDomainEventBus,
        permission_checker: PermissionCheckerPort,
    ) -> AssignRoleHandler:
        return AssignRoleHandler(
            user_repo=user_repo,
            role_repo=role_repo,
            event_bus=event_bus,
            permission_checker=permission_checker,
        )

    async def test_assign_role_success(
        self, handler: AssignRoleHandler, make_user, make_role, user_repo: SqlUserRepository
    ) -> None:
        user = await make_user()
        role = await make_role(name="moderator")

        cmd = AssignRoleCommand(caller_id=str(user.id), user_id=str(user.id), role_id=str(role.id))
        await handler.handle(cmd)

        updated = await user_repo.get_by_id(user.id)
        assert updated is not None
        assert role.id in updated.role_ids

    async def test_assign_duplicate_role_raises(
        self, handler: AssignRoleHandler, make_user, make_role, user_repo: SqlUserRepository
    ) -> None:
        user = await make_user()
        role = await make_role(name="dup-role")

        cmd = AssignRoleCommand(caller_id=str(user.id), user_id=str(user.id), role_id=str(role.id))
        await handler.handle(cmd)

        # Повторное назначение → exception
        with pytest.raises(DuplicateRoleException):
            await handler.handle(cmd)
