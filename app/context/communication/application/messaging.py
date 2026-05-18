"""
Messaging-конфигурация Communication BC.

BC описывает:
- в какой топик публикует свои доменные события (`communication.events`);
- на какие топики других BC он подписан.

Communication BC слушает ``project.events``, чтобы автоматически
поддерживать жизненный цикл проектных чатов (создание/архивация/
синхронизация участников). См. docs/events/communication-events.md.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.application.messaging.broker_domain_event_bus import (
    BrokerDomainEventBus,
)
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.messaging.subscription import (
    MessageHandlerFn,
    Subscription,
)
from app.shared.application.ports.messaging.message_broker_port import (
    MessageBrokerPort,
)

if TYPE_CHECKING:
    from app.core.di.container import Container


# --- Публикация ---

COMMUNICATION_EVENTS_TOPIC = "communication.events"
PROJECT_EVENTS_TOPIC = "project.events"


def build_communication_event_bus(broker: MessageBrokerPort) -> DomainEventBus:
    """Создать DomainEventBus Communication BC."""
    return BrokerDomainEventBus(broker=broker, topic=COMMUNICATION_EVENTS_TOPIC)


# --- Подписки ---


def communication_subscriptions(container: "Container") -> list[Subscription]:
    """
    Подписки Communication BC на топики других BC.

    Communication BC реагирует на события Project BC, чтобы синхронизировать
    проектные чаты с проектом:

    * ``ProjectMemberJoined`` — добавляет участника в чат / создаёт чат,
      когда участников становится ≥ 2.
    * ``ProjectMemberRemoved`` — удаляет участника из чата.
    * ``ProjectArchived`` / ``ProjectDeletionRequested`` — архивирует чат
      (сообщения сохраняются).
    * ``ProjectRestored`` / ``ProjectReactivated`` — разархивирует чат.
    """
    from app.context.communication.application.event_handlers.on_project_archived_archive_chat import (
        OnProjectArchivedArchiveChat,
    )
    from app.context.communication.application.event_handlers.on_project_deletion_requested_archive_chat import (
        OnProjectDeletionRequestedArchiveChat,
    )
    from app.context.communication.application.event_handlers.on_project_member_joined_sync_chat import (
        OnProjectMemberJoinedSyncChat,
    )
    from app.context.communication.application.event_handlers.on_project_member_removed_sync_chat import (
        OnProjectMemberRemovedSyncChat,
    )
    from app.context.communication.application.event_handlers.on_project_restored_restore_chat import (
        OnProjectRestoredRestoreChat,
    )

    def _build_on_project_member_joined(session: AsyncSession) -> MessageHandlerFn:
        chat_repo = container.chat_repo(session=session)
        project_repo = container.project_repo(session=session)
        project_membership_repo = container.project_membership_repo(session=session)
        project_provider_inst = container.project_provider(repo=project_repo)
        project_membership_provider_inst = container.project_membership_provider(
            repo=project_membership_repo,
        )
        handler = OnProjectMemberJoinedSyncChat(
            chat_repo=chat_repo,
            project_provider=project_provider_inst,
            project_membership_provider=project_membership_provider_inst,
            event_bus=container.communication_event_bus(),
        )

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_project_member_removed(session: AsyncSession) -> MessageHandlerFn:
        chat_repo = container.chat_repo(session=session)
        handler = OnProjectMemberRemovedSyncChat(
            chat_repo=chat_repo,
            event_bus=container.communication_event_bus(),
        )

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_project_archived(session: AsyncSession) -> MessageHandlerFn:
        chat_repo = container.chat_repo(session=session)
        handler = OnProjectArchivedArchiveChat(
            chat_repo=chat_repo,
            event_bus=container.communication_event_bus(),
        )

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_project_deletion_requested(
        session: AsyncSession,
    ) -> MessageHandlerFn:
        chat_repo = container.chat_repo(session=session)
        handler = OnProjectDeletionRequestedArchiveChat(
            chat_repo=chat_repo,
            event_bus=container.communication_event_bus(),
        )

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_project_restored(session: AsyncSession) -> MessageHandlerFn:
        chat_repo = container.chat_repo(session=session)
        handler = OnProjectRestoredRestoreChat(
            chat_repo=chat_repo,
            event_bus=container.communication_event_bus(),
        )

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    return [
        Subscription(
            topic=PROJECT_EVENTS_TOPIC,
            group_id="communication-bc--project-member-joined",
            build_handler=_build_on_project_member_joined,
        ),
        Subscription(
            topic=PROJECT_EVENTS_TOPIC,
            group_id="communication-bc--project-member-removed",
            build_handler=_build_on_project_member_removed,
        ),
        Subscription(
            topic=PROJECT_EVENTS_TOPIC,
            group_id="communication-bc--project-archived",
            build_handler=_build_on_project_archived,
        ),
        Subscription(
            topic=PROJECT_EVENTS_TOPIC,
            group_id="communication-bc--project-deletion-requested",
            build_handler=_build_on_project_deletion_requested,
        ),
        Subscription(
            topic=PROJECT_EVENTS_TOPIC,
            group_id="communication-bc--project-restored",
            build_handler=_build_on_project_restored,
        ),
    ]
