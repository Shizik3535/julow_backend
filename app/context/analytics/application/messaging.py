"""
Messaging-конфигурация Analytics BC.

BC описывает:
    - в какой топик публикует свои доменные события (`analytics.events`);
    - на какие топики других BC он подписан.

Analytics BC сам потребляет данные через `AnalyticsQueryExecutorPort`
(синхронный запрос ACL-резолверам). Подписки на события других BC по
дефолту не нужны: данные подтягиваются on-demand при выполнении запроса.
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

ANALYTICS_EVENTS_TOPIC = "analytics.events"


def build_analytics_event_bus(broker: MessageBrokerPort) -> DomainEventBus:
    """Создать DomainEventBus Analytics BC."""
    return BrokerDomainEventBus(broker=broker, topic=ANALYTICS_EVENTS_TOPIC)


# --- Подписки ---


def analytics_subscriptions(container: "Container") -> list[Subscription]:
    """Analytics BC не подписывается на события других BC (см. docs/events)."""
    return []
