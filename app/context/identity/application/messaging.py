"""
Messaging-конфигурация Identity BC.

BC сам описывает:
- в какой топик публикует свои доменные события (через DomainEventBus);
- на какие топики других BC он подписан (через список Subscription).

Core/DI собирает эти описания и регистрирует их в брокере —
сам BC не знает о деталях Kafka/DI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.shared.application.messaging.broker_domain_event_bus import BrokerDomainEventBus
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.messaging.subscription import Subscription
from app.shared.application.ports.messaging.message_broker_port import MessageBrokerPort

if TYPE_CHECKING:
    from app.core.di.container import Container


IDENTITY_EVENTS_TOPIC = "identity.events"


def build_identity_event_bus(broker: MessageBrokerPort) -> DomainEventBus:
    """Создать DomainEventBus Identity BC (публикует в ``identity.events``)."""
    return BrokerDomainEventBus(broker=broker, topic=IDENTITY_EVENTS_TOPIC)


def identity_subscriptions(container: "Container") -> list[Subscription]:
    """
    Подписки Identity BC на топики других BC.

    Сейчас Identity BC не реагирует на внешние события и пуст.
    При появлении подписок — добавлять сюда ``Subscription(...)``.
    """
    return []
