"""
Messaging-конфигурация Workspace BC.

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

WORKSPACE_EVENTS_TOPIC = "workspace.events"
WORKSPACE_CONSUMER_GROUP = "workspace-bc"

ORGANIZATION_EVENTS_TOPIC = "organization.events"


def build_workspace_event_bus(broker: MessageBrokerPort) -> DomainEventBus:
    """Создать DomainEventBus Workspace BC (публикует в ``workspace.events``)."""
    return BrokerDomainEventBus(broker=broker, topic=WORKSPACE_EVENTS_TOPIC)


def workspace_subscriptions(container: "Container") -> list[Subscription]:
    """
    Подписки Workspace BC на топики других BC и свой топик.

    - Organization BC → OrgMemberJoined: автодобавление участников (auto_add_from_org).
    - Workspace BC (self) → SecurityPolicyChanged: каскад политики безопасности.
    - Workspace BC (self) → MembershipPolicyChanged: каскад политики членства.
    """
    from app.context.workspace.application.event_handlers.on_org_member_joined_auto_add import (
        OnOrgMemberJoinedAutoAdd,
    )
    from app.context.workspace.application.event_handlers.on_security_policy_changed_cascade import (
        OnSecurityPolicyCascade,
    )
    from app.context.workspace.application.event_handlers.on_membership_policy_changed_cascade import (
        OnMembershipPolicyCascade,
    )

    def _build_on_org_member_joined(session: AsyncSession) -> MessageHandlerFn:
        handler = OnOrgMemberJoinedAutoAdd(
            ws_repo=container.workspace_repo(session=session),
            membership_repo=container.workspace_membership_repo(session=session),
            role_repo=container.workspace_role_repo(session=session),
        )

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_security_policy_cascade(session: AsyncSession) -> MessageHandlerFn:
        handler = OnSecurityPolicyCascade(
            ws_repo=container.workspace_repo(session=session),
        )

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_membership_policy_cascade(session: AsyncSession) -> MessageHandlerFn:
        handler = OnMembershipPolicyCascade(
            ws_repo=container.workspace_repo(session=session),
        )

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    return [
        Subscription(
            topic=ORGANIZATION_EVENTS_TOPIC,
            group_id=WORKSPACE_CONSUMER_GROUP,
            build_handler=_build_on_org_member_joined,
        ),
        Subscription(
            topic=WORKSPACE_EVENTS_TOPIC,
            group_id=WORKSPACE_CONSUMER_GROUP,
            build_handler=_build_on_security_policy_cascade,
        ),
        Subscription(
            topic=WORKSPACE_EVENTS_TOPIC,
            group_id=WORKSPACE_CONSUMER_GROUP,
            build_handler=_build_on_membership_policy_cascade,
        ),
    ]
