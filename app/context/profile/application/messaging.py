"""
Messaging-конфигурация Profile BC.

BC сам описывает:
- в какой топик публикует свои доменные события;
- на какие топики других BC он подписан.

Core/DI собирает эти описания и регистрирует их в брокере.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.context.identity.application.messaging import IDENTITY_EVENTS_TOPIC
from app.context.profile.application.event_handlers.on_user_deleted_delete_profile import (
    OnUserDeletedDeleteProfile,
)
from app.context.profile.application.event_handlers.on_user_registered_create_profile import (
    OnUserRegisteredCreateProfile,
)
from app.shared.application.messaging.broker_domain_event_bus import BrokerDomainEventBus
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.messaging.subscription import MessageHandlerFn, Subscription
from app.shared.application.ports.messaging.message_broker_port import MessageBrokerPort

if TYPE_CHECKING:
    from app.core.di.container import Container


PROFILE_EVENTS_TOPIC = "profile.events"


def build_profile_event_bus(broker: MessageBrokerPort) -> DomainEventBus:
    """Создать DomainEventBus Profile BC (публикует в ``profile.events``)."""
    return BrokerDomainEventBus(broker=broker, topic=PROFILE_EVENTS_TOPIC)


def profile_subscriptions(container: "Container") -> list[Subscription]:
    """Подписки Profile BC на топики других BC."""

    def _build_on_user_registered(session: AsyncSession) -> MessageHandlerFn:
        profile_repo = container.profile_repo(session=session)
        handler = OnUserRegisteredCreateProfile(profile_repo=profile_repo)

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_user_deleted(session: AsyncSession) -> MessageHandlerFn:
        profile_repo = container.profile_repo(session=session)
        handler = OnUserDeletedDeleteProfile(profile_repo=profile_repo)

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    return [
        Subscription(
            topic=IDENTITY_EVENTS_TOPIC,
            group_id="profile-bc--user-registered",
            build_handler=_build_on_user_registered,
        ),
        Subscription(
            topic=IDENTITY_EVENTS_TOPIC,
            group_id="profile-bc--user-deleted",
            build_handler=_build_on_user_deleted,
        ),
    ]
