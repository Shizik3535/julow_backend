"""
Messaging-конфигурация Task BC.

BC описывает:
- в какой топик публикует свои доменные события;
- на какие топики других BC он подписан.
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


# --- Публикация ---

TASK_EVENTS_TOPIC = "task.events"


def build_task_event_bus(broker: MessageBrokerPort) -> DomainEventBus:
    """Создать DomainEventBus Task BC."""
    return BrokerDomainEventBus(broker=broker, topic=TASK_EVENTS_TOPIC)


# --- Подписки ---

TASK_CONSUMER_GROUP = "task-bc"


def task_subscriptions(container: "Container") -> list[Subscription]:
    """Подписки Task BC на топики других BC."""

    from app.context.project.application.messaging import PROJECT_EVENTS_TOPIC
    from app.context.task.application.event_handlers.on_project_archived import OnProjectArchived
    from app.context.task.application.event_handlers.on_sprint_completed import OnSprintCompleted
    from app.context.task.application.event_handlers.on_sprint_cancelled import OnSprintCancelled
    from app.context.task.application.event_handlers.on_workflow_status_removed import OnWorkflowStatusRemoved
    from app.context.task.application.event_handlers.on_epic_cancelled import OnEpicCancelled

    def _build_project_events_handler(session: AsyncSession) -> MessageHandlerFn:
        task_repo = container.task_repo(session=session)
        board_port = container.task_board_port()
        event_bus = build_task_event_bus(container.message_broker_port())

        handlers = [
            OnProjectArchived(task_repo=task_repo, event_bus=event_bus),
            OnSprintCompleted(task_repo=task_repo, event_bus=event_bus),
            OnSprintCancelled(task_repo=task_repo, event_bus=event_bus),
            OnWorkflowStatusRemoved(task_repo=task_repo, board_port=board_port, event_bus=event_bus),
            OnEpicCancelled(task_repo=task_repo, event_bus=event_bus),
        ]

        async def _run(message: dict[str, Any]) -> None:
            for handler in handlers:
                await handler.handle(message)

        return _run

    return [
        Subscription(
            topic=PROJECT_EVENTS_TOPIC,
            group_id=TASK_CONSUMER_GROUP,
            build_handler=_build_project_events_handler,
        ),
    ]
