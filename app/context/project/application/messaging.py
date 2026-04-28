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

WORKSPACE_EVENTS_TOPIC = "workspace.events"


def build_project_event_bus(broker: MessageBrokerPort) -> DomainEventBus:
    """Создать DomainEventBus Project BC (публикует в ``project.events``)."""
    return BrokerDomainEventBus(broker=broker, topic=PROJECT_EVENTS_TOPIC)


def project_subscriptions(container: "Container") -> list[Subscription]:
    """
    Подписки Project BC на топики других BC и свой топик.

    - Workspace BC → WorkspaceArchived: архивирование проектов.
    - Workspace BC → WorkspaceDeletionRequested: удаление проектов.
    - Workspace BC → WorkspaceRestored: восстановление проектов.
    - Workspace BC → WorkspaceMemberRemoved: удаление участников из проектов.
    - Project BC (self) → OnAutomationRuleTriggered: запуск автоматизаций.
    """
    from app.context.project.application.event_handlers.on_workspace_archived_cascade import (
        OnWorkspaceArchivedCascade,
    )
    from app.context.project.application.event_handlers.on_workspace_deletion_requested_cascade import (
        OnWorkspaceDeletionRequestedCascade,
    )
    from app.context.project.application.event_handlers.on_workspace_restored_cascade import (
        OnWorkspaceRestoredCascade,
    )
    from app.context.project.application.event_handlers.on_workspace_member_removed_cascade import (
        OnWorkspaceMemberRemovedCascade,
    )

    def _build_on_workspace_archived(session: AsyncSession) -> MessageHandlerFn:
        handler = OnWorkspaceArchivedCascade(
            project_repo=container.project_repo(session=session),
            event_bus=container.project_event_bus(),
        )

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_workspace_deletion_requested(session: AsyncSession) -> MessageHandlerFn:
        handler = OnWorkspaceDeletionRequestedCascade(
            project_repo=container.project_repo(session=session),
            event_bus=container.project_event_bus(),
        )

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_workspace_restored(session: AsyncSession) -> MessageHandlerFn:
        handler = OnWorkspaceRestoredCascade(
            project_repo=container.project_repo(session=session),
            event_bus=container.project_event_bus(),
        )

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_workspace_member_removed(session: AsyncSession) -> MessageHandlerFn:
        handler = OnWorkspaceMemberRemovedCascade(
            project_repo=container.project_repo(session=session),
            membership_repo=container.project_membership_repo(session=session),
            event_bus=container.project_event_bus(),
        )

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_automation_rule_triggered(session: AsyncSession) -> MessageHandlerFn:
        async def _run(message: dict[str, Any]) -> None:
            # TODO: реализовать OnAutomationRuleTriggered handler
            pass

        return _run

    return [
        Subscription(
            topic=WORKSPACE_EVENTS_TOPIC,
            group_id="project-bc--workspace-archived",
            build_handler=_build_on_workspace_archived,
        ),
        Subscription(
            topic=WORKSPACE_EVENTS_TOPIC,
            group_id="project-bc--workspace-deletion-requested",
            build_handler=_build_on_workspace_deletion_requested,
        ),
        Subscription(
            topic=WORKSPACE_EVENTS_TOPIC,
            group_id="project-bc--workspace-restored",
            build_handler=_build_on_workspace_restored,
        ),
        Subscription(
            topic=WORKSPACE_EVENTS_TOPIC,
            group_id="project-bc--workspace-member-removed",
            build_handler=_build_on_workspace_member_removed,
        ),
        Subscription(
            topic=PROJECT_EVENTS_TOPIC,
            group_id="project-bc--automation-rule-triggered",
            build_handler=_build_on_automation_rule_triggered,
        ),
    ]
