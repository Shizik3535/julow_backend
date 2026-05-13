"""
Messaging-конфигурация TimeTracking BC.

BC описывает:
- в какой топик публикует свои доменные события;
- на какие топики других BC он подписан (нет — см. docs/events/timetracking-events.md).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.shared.application.messaging.broker_domain_event_bus import BrokerDomainEventBus
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.messaging.subscription import Subscription
from app.shared.application.ports.messaging.message_broker_port import MessageBrokerPort

if TYPE_CHECKING:
    from app.core.di.container import Container


# --- Публикация ---

TIMETRACKING_EVENTS_TOPIC = "timetracking.events"


def build_timetracking_event_bus(broker: MessageBrokerPort) -> DomainEventBus:
    """Создать DomainEventBus TimeTracking BC."""
    return BrokerDomainEventBus(broker=broker, topic=TIMETRACKING_EVENTS_TOPIC)


# --- Подписки ---


def timetracking_subscriptions(container: "Container") -> list[Subscription]:
    """TimeTracking BC не подписывается на события других BC (см. docs/events)."""
    return []
