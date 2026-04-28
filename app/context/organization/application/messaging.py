"""
Messaging-конфигурация Organization BC.

BC сам описывает:
- в какой топик публикует свои доменные события (через DomainEventBus);
- на какие топики других BC он подписан (через список Subscription).

Core/DI собирает эти описания и регистрирует их в брокере —
сам BC не знает о деталях Kafka/DI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.application.messaging.broker_domain_event_bus import BrokerDomainEventBus
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.messaging.subscription import MessageHandlerFn, Subscription
from app.shared.application.ports.messaging.message_broker_port import MessageBrokerPort

if TYPE_CHECKING:
    from app.core.di.container import Container

ORGANIZATION_EVENTS_TOPIC = "organization.events"

IDENTITY_EVENTS_TOPIC = "identity.events"


def build_organization_event_bus(broker: MessageBrokerPort) -> DomainEventBus:
    """Создать DomainEventBus Organization BC (публикует в ``organization.events``)."""
    return BrokerDomainEventBus(broker=broker, topic=ORGANIZATION_EVENTS_TOPIC)


def organization_subscriptions(container: "Container") -> list[Subscription]:
    """
    Подписки Organization BC на топики других BC.

    - Identity BC → AccountDeletionRequested: очистка членств удалённого пользователя.
    - Identity BC → UserDeleted: окончательная очистка членств.
    """
    from app.context.organization.application.event_handlers.on_account_deletion_requested_cleanup_memberships import (
        OnAccountDeletionRequestedCleanupMemberships,
    )
    from app.context.organization.application.event_handlers.on_user_deleted_cleanup_memberships import (
        OnUserDeletedCleanupMemberships,
    )

    def _build_on_account_deletion(session: AsyncSession) -> MessageHandlerFn:
        membership_repo = container.org_membership_repo(session=session)
        handler = OnAccountDeletionRequestedCleanupMemberships(
            membership_repo=membership_repo,
        )

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_user_deleted(session: AsyncSession) -> MessageHandlerFn:
        membership_repo = container.org_membership_repo(session=session)
        handler = OnUserDeletedCleanupMemberships(
            membership_repo=membership_repo,
        )

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    return [
        Subscription(
            topic=IDENTITY_EVENTS_TOPIC,
            group_id="organization-bc--account-deletion",
            build_handler=_build_on_account_deletion,
        ),
        Subscription(
            topic=IDENTITY_EVENTS_TOPIC,
            group_id="organization-bc--user-deleted",
            build_handler=_build_on_user_deleted,
        ),
    ]
