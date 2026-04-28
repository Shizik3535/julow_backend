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

IDENTITY_EVENTS_TOPIC = "identity.events"
ORGANIZATION_EVENTS_TOPIC = "organization.events"


def build_workspace_event_bus(broker: MessageBrokerPort) -> DomainEventBus:
    """Создать DomainEventBus Workspace BC (публикует в ``workspace.events``)."""
    return BrokerDomainEventBus(broker=broker, topic=WORKSPACE_EVENTS_TOPIC)


def workspace_subscriptions(container: "Container") -> list[Subscription]:
    """
    Подписки Workspace BC на топики других BC и свой топик.

    - Identity BC → UserDeleted: очистка членств удалённого пользователя.
    - Organization BC → OrgMemberJoined: автодобавление участников (auto_add_from_org).
    - Organization BC → OrgMemberRemoved: каскадное удаление из workspace.
    - Organization BC → OrgMemberDeactivated: каскадная деактивация в workspace.
    - Workspace BC (self) → SecurityPolicyChanged: каскад политики безопасности.
    - Workspace BC (self) → MembershipPolicyChanged: каскад политики членства.
    """
    from app.context.workspace.application.event_handlers.on_user_deleted_cleanup_memberships import (
        OnUserDeletedCleanupMemberships,
    )
    from app.context.workspace.application.event_handlers.on_org_member_removed_cascade import (
        OnOrgMemberRemovedCascade,
    )
    from app.context.workspace.application.event_handlers.on_org_member_deactivated_cascade import (
        OnOrgMemberDeactivatedCascade,
    )
    from app.context.workspace.application.event_handlers.on_org_member_joined_auto_add import (
        OnOrgMemberJoinedAutoAdd,
    )
    from app.context.workspace.application.event_handlers.on_security_policy_changed_cascade import (
        OnSecurityPolicyCascade,
    )
    from app.context.workspace.application.event_handlers.on_membership_policy_changed_cascade import (
        OnMembershipPolicyCascade,
    )

    def _build_on_user_deleted(session: AsyncSession) -> MessageHandlerFn:
        membership_repo = container.workspace_membership_repo(session=session)
        handler = OnUserDeletedCleanupMemberships(
            membership_repo=membership_repo,
        )

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_org_member_removed(session: AsyncSession) -> MessageHandlerFn:
        membership_repo = container.workspace_membership_repo(session=session)
        workspace_repo = container.workspace_repo(session=session)
        handler = OnOrgMemberRemovedCascade(
            membership_repo=membership_repo,
            workspace_repo=workspace_repo,
        )

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_org_member_deactivated(session: AsyncSession) -> MessageHandlerFn:
        membership_repo = container.workspace_membership_repo(session=session)
        workspace_repo = container.workspace_repo(session=session)
        handler = OnOrgMemberDeactivatedCascade(
            membership_repo=membership_repo,
            workspace_repo=workspace_repo,
        )

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

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
            topic=IDENTITY_EVENTS_TOPIC,
            group_id="workspace-bc--user-deleted",
            build_handler=_build_on_user_deleted,
        ),
        Subscription(
            topic=ORGANIZATION_EVENTS_TOPIC,
            group_id="workspace-bc--org-member-removed",
            build_handler=_build_on_org_member_removed,
        ),
        Subscription(
            topic=ORGANIZATION_EVENTS_TOPIC,
            group_id="workspace-bc--org-member-deactivated",
            build_handler=_build_on_org_member_deactivated,
        ),
        Subscription(
            topic=ORGANIZATION_EVENTS_TOPIC,
            group_id="workspace-bc--org-member-joined",
            build_handler=_build_on_org_member_joined,
        ),
        Subscription(
            topic=WORKSPACE_EVENTS_TOPIC,
            group_id="workspace-bc--security-policy-cascade",
            build_handler=_build_on_security_policy_cascade,
        ),
        Subscription(
            topic=WORKSPACE_EVENTS_TOPIC,
            group_id="workspace-bc--membership-policy-cascade",
            build_handler=_build_on_membership_policy_cascade,
        ),
    ]
