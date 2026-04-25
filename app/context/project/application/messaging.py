"""
Messaging-конфигурация Project BC.

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

PROJECT_EVENTS_TOPIC = "project.events"
PROJECT_CONSUMER_GROUP = "project-bc"

WORKSPACE_EVENTS_TOPIC = "workspace.events"


def build_project_event_bus(broker: MessageBrokerPort) -> DomainEventBus:
    """Создать DomainEventBus Project BC (публикует в ``project.events``)."""
    return BrokerDomainEventBus(broker=broker, topic=PROJECT_EVENTS_TOPIC)


def project_subscriptions(container: "Container") -> list[Subscription]:
    """
    Подписки Project BC на топики других BC и свой топик.

    - Workspace BC → OnWorkspaceMemberRemoved: деактивация участников проекта.
    - Project BC (self) → OnAutomationRuleTriggered: запуск автоматизаций.
    """
    def _build_on_workspace_member_removed(session: AsyncSession) -> MessageHandlerFn:
        async def _run(message: dict[str, Any]) -> None:
            # TODO: реализовать OnWorkspaceMemberRemoved handler
            pass

        return _run

    def _build_on_automation_rule_triggered(session: AsyncSession) -> MessageHandlerFn:
        async def _run(message: dict[str, Any]) -> None:
            # TODO: реализовать OnAutomationRuleTriggered handler
            pass

        return _run

    return [
        Subscription(
            topic=WORKSPACE_EVENTS_TOPIC,
            group_id=PROJECT_CONSUMER_GROUP,
            build_handler=_build_on_workspace_member_removed,
        ),
        Subscription(
            topic=PROJECT_EVENTS_TOPIC,
            group_id=PROJECT_CONSUMER_GROUP,
            build_handler=_build_on_automation_rule_triggered,
        ),
    ]
