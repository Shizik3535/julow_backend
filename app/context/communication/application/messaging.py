"""
Messaging-конфигурация Communication BC.

BC описывает:
- в какой топик публикует свои доменные события (`communication.events`);
- на какие топики других BC он подписан.

Communication BC по спецификации не подписывается на события других BC
(см. docs/events/communication-events.md).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.shared.application.messaging.broker_domain_event_bus import (
    BrokerDomainEventBus,
)
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.messaging.subscription import Subscription
from app.shared.application.ports.messaging.message_broker_port import (
    MessageBrokerPort,
)

if TYPE_CHECKING:
    from app.core.di.container import Container


# --- Публикация ---

COMMUNICATION_EVENTS_TOPIC = "communication.events"


def build_communication_event_bus(broker: MessageBrokerPort) -> DomainEventBus:
    """Создать DomainEventBus Communication BC."""
    return BrokerDomainEventBus(broker=broker, topic=COMMUNICATION_EVENTS_TOPIC)


# --- Подписки ---


def communication_subscriptions(container: "Container") -> list[Subscription]:
    """
    Подписки Communication BC на топики других BC.

    Согласно docs/events/communication-events.md, Communication BC
    не подписывается на события других BC.
    """
    return []
