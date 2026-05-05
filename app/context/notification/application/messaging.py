"""
Messaging-конфигурация Notification BC.

BC описывает:
- в какой топик публикует свои доменные события;
- на какие топики других BC он подписан.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.shared.application.messaging.broker_domain_event_bus import BrokerDomainEventBus
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.messaging.subscription import MessageHandlerFn, Subscription
from app.shared.application.ports.messaging.message_broker_port import MessageBrokerPort
from app.context.notification.domain.value_objects.channel_type import ChannelType
from app.context.notification.domain.value_objects.notification_priority import NotificationPriority
from app.context.notification.domain.value_objects.notification_type import NotificationType

if TYPE_CHECKING:
    from app.core.di.container import Container


# --- Публикация ---

NOTIFICATION_EVENTS_TOPIC = "notification.events"

logger = get_logger(__name__)


def build_notification_event_bus(broker: MessageBrokerPort) -> DomainEventBus:
    """Создать DomainEventBus Notification BC."""
    return BrokerDomainEventBus(broker=broker, topic=NOTIFICATION_EVENTS_TOPIC)


# --- Подписки ---

IDENTITY_EVENTS_TOPIC = "identity.events"
ORGANIZATION_EVENTS_TOPIC = "organization.events"
WORKSPACE_EVENTS_TOPIC = "workspace.events"
PROJECT_EVENTS_TOPIC = "project.events"
TASK_EVENTS_TOPIC = "task.events"


def notification_subscriptions(container: "Container") -> list[Subscription]:
    """Подписки Notification BC на топики других BC."""

    # --- Identity BC ---

    from app.context.notification.application.event_handlers.on_user_registered_create_preferences import (
        OnUserRegisteredCreatePreferences,
    )
    from app.context.notification.application.event_handlers.on_password_changed_notify import (
        OnPasswordChangedNotify,
    )
    from app.context.notification.application.event_handlers.on_new_device_login_notify import (
        OnNewDeviceLoginNotify,
    )
    from app.context.notification.application.event_handlers.on_auth_factor_changed_notify import (
        OnAuthFactorChangedNotify,
    )
    from app.context.notification.application.event_handlers.on_user_deleted_cleanup import (
        OnUserDeletedCleanup,
    )
    from app.context.notification.application.event_handlers.on_email_confirmed_send_welcome import (
        OnEmailConfirmedSendWelcome,
    )

    def _build_on_user_registered(session: AsyncSession) -> MessageHandlerFn:
        repo = container.notification_preferences_repo(session=session)
        handler = OnUserRegisteredCreatePreferences(preferences_repo=repo)

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_email_confirmed(session: AsyncSession) -> MessageHandlerFn:
        repo = container.notification_repo(session=session)
        handler = OnEmailConfirmedSendWelcome(notification_repo=repo, event_bus=container.notification_event_bus())

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_password_changed(session: AsyncSession) -> MessageHandlerFn:
        repo = container.notification_repo(session=session)
        handler = OnPasswordChangedNotify(notification_repo=repo, event_bus=container.notification_event_bus())

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_new_device_login(session: AsyncSession) -> MessageHandlerFn:
        repo = container.notification_repo(session=session)
        handler = OnNewDeviceLoginNotify(notification_repo=repo, event_bus=container.notification_event_bus())

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_auth_factor_changed(session: AsyncSession) -> MessageHandlerFn:
        repo = container.notification_repo(session=session)
        handler = OnAuthFactorChangedNotify(notification_repo=repo, event_bus=container.notification_event_bus())

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_user_deleted(session: AsyncSession) -> MessageHandlerFn:
        preferences_repo = container.notification_preferences_repo(session=session)
        device_token_repo = container.device_token_repo(session=session)
        handler = OnUserDeletedCleanup(
            preferences_repo=preferences_repo,
            device_token_repo=device_token_repo,
        )

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    # --- Organization BC ---

    from app.context.notification.application.event_handlers.on_org_invitation_sent_notify import (
        OnOrgInvitationSentNotify,
    )

    def _build_on_org_invitation(session: AsyncSession) -> MessageHandlerFn:
        notification_repo = container.notification_repo(session=session)
        preferences_repo = container.notification_preferences_repo(session=session)
        handler = OnOrgInvitationSentNotify(
            notification_repo=notification_repo,
            event_bus=container.notification_event_bus(),
            preferences_repo=preferences_repo,
        )

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    # --- Workspace BC ---

    from app.context.notification.application.event_handlers.on_workspace_invitation_sent_notify import (
        OnWorkspaceInvitationSentNotify,
    )

    def _build_on_workspace_invitation(session: AsyncSession) -> MessageHandlerFn:
        repo = container.notification_repo(session=session)
        handler = OnWorkspaceInvitationSentNotify(notification_repo=repo, event_bus=container.notification_event_bus())

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    # --- Project BC ---

    from app.context.notification.application.event_handlers.on_project_member_joined_notify import (
        OnProjectMemberJoinedNotify,
    )
    from app.context.notification.application.event_handlers.on_sprint_started_notify import (
        OnSprintStartedNotify,
    )
    from app.context.notification.application.event_handlers.on_sprint_completed_notify import (
        OnSprintCompletedNotify,
    )
    from app.context.notification.application.event_handlers.on_project_deadline_approaching_notify import (
        OnProjectDeadlineApproachingNotify,
    )
    from app.context.notification.application.event_handlers.on_project_overdue_notify import (
        OnProjectOverdueNotify,
    )

    def _build_on_project_member_joined(session: AsyncSession) -> MessageHandlerFn:
        repo = container.notification_repo(session=session)
        handler = OnProjectMemberJoinedNotify(notification_repo=repo, event_bus=container.notification_event_bus())

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_project_deadline_approaching(session: AsyncSession) -> MessageHandlerFn:
        repo = container.notification_repo(session=session)
        project_membership_repo = container.project_membership_repo(session=session)
        project_membership_provider = container.project_membership_provider(repo=project_membership_repo)
        project_repo = container.project_repo(session=session)
        project_provider_inst = container.project_provider(repo=project_repo)
        project_member_port = container.notification_project_member_port(
            project_membership_provider=project_membership_provider,
            project_provider=project_provider_inst,
        )
        handler = OnProjectDeadlineApproachingNotify(notification_repo=repo, event_bus=container.notification_event_bus(), project_member_port=project_member_port)

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_project_overdue(session: AsyncSession) -> MessageHandlerFn:
        repo = container.notification_repo(session=session)
        project_membership_repo = container.project_membership_repo(session=session)
        project_membership_provider = container.project_membership_provider(repo=project_membership_repo)
        project_repo = container.project_repo(session=session)
        project_provider_inst = container.project_provider(repo=project_repo)
        project_member_port = container.notification_project_member_port(
            project_membership_provider=project_membership_provider,
            project_provider=project_provider_inst,
        )
        handler = OnProjectOverdueNotify(notification_repo=repo, event_bus=container.notification_event_bus(), project_member_port=project_member_port)

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_sprint_started(session: AsyncSession) -> MessageHandlerFn:
        repo = container.notification_repo(session=session)
        handler = OnSprintStartedNotify(notification_repo=repo, event_bus=container.notification_event_bus())

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_sprint_completed(session: AsyncSession) -> MessageHandlerFn:
        repo = container.notification_repo(session=session)
        handler = OnSprintCompletedNotify(notification_repo=repo, event_bus=container.notification_event_bus())

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    # --- Task BC ---

    from app.context.notification.application.event_handlers.on_task_assigned_notify import (
        OnTaskAssignedNotify,
    )
    from app.context.notification.application.event_handlers.on_task_unassigned_notify import (
        OnTaskUnassignedNotify,
    )
    from app.context.notification.application.event_handlers.on_task_status_changed_notify import (
        OnTaskStatusChangedNotify,
    )
    from app.context.notification.application.event_handlers.on_task_comment_added_notify import (
        OnTaskCommentAddedNotify,
    )
    from app.context.notification.application.event_handlers.on_task_deadline_approaching_notify import (
        OnTaskDeadlineApproachingNotify,
    )
    from app.context.notification.application.event_handlers.on_task_overdue_notify import (
        OnTaskOverdueNotify,
    )
    from app.context.notification.application.event_handlers.on_task_info_changed_notify import (
        OnTaskInfoChangedNotify,
    )

    def _build_on_task_assigned(session: AsyncSession) -> MessageHandlerFn:
        repo = container.notification_repo(session=session)
        handler = OnTaskAssignedNotify(notification_repo=repo, event_bus=container.notification_event_bus())

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_task_unassigned(session: AsyncSession) -> MessageHandlerFn:
        repo = container.notification_repo(session=session)
        handler = OnTaskUnassignedNotify(notification_repo=repo, event_bus=container.notification_event_bus())

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_task_status_changed(session: AsyncSession) -> MessageHandlerFn:
        repo = container.notification_repo(session=session)
        task_repo = container.task_repo(session=session)
        task_participant_provider = container.task_participant_provider(repo=task_repo)
        task_participant_port = container.notification_task_participant_port(task_participant_provider=task_participant_provider)
        handler = OnTaskStatusChangedNotify(notification_repo=repo, event_bus=container.notification_event_bus(), task_participant_port=task_participant_port)

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_task_comment_added(session: AsyncSession) -> MessageHandlerFn:
        repo = container.notification_repo(session=session)
        task_repo = container.task_repo(session=session)
        task_participant_provider = container.task_participant_provider(repo=task_repo)
        task_participant_port = container.notification_task_participant_port(task_participant_provider=task_participant_provider)
        handler = OnTaskCommentAddedNotify(notification_repo=repo, event_bus=container.notification_event_bus(), task_participant_port=task_participant_port)

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_task_deadline_approaching(session: AsyncSession) -> MessageHandlerFn:
        repo = container.notification_repo(session=session)
        task_repo = container.task_repo(session=session)
        task_participant_provider = container.task_participant_provider(repo=task_repo)
        task_participant_port = container.notification_task_participant_port(task_participant_provider=task_participant_provider)
        handler = OnTaskDeadlineApproachingNotify(notification_repo=repo, event_bus=container.notification_event_bus(), task_participant_port=task_participant_port)

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_task_overdue(session: AsyncSession) -> MessageHandlerFn:
        repo = container.notification_repo(session=session)
        task_repo = container.task_repo(session=session)
        task_participant_provider = container.task_participant_provider(repo=task_repo)
        task_participant_port = container.notification_task_participant_port(task_participant_provider=task_participant_provider)
        handler = OnTaskOverdueNotify(notification_repo=repo, event_bus=container.notification_event_bus(), task_participant_port=task_participant_port)

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_task_info_changed(session: AsyncSession) -> MessageHandlerFn:
        repo = container.notification_repo(session=session)
        task_repo = container.task_repo(session=session)
        task_participant_provider = container.task_participant_provider(repo=task_repo)
        task_participant_port = container.notification_task_participant_port(task_participant_provider=task_participant_provider)
        handler = OnTaskInfoChangedNotify(notification_repo=repo, event_bus=container.notification_event_bus(), task_participant_port=task_participant_port)

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    # --- Notification BC (self-subscription) ---

    from app.context.notification.application.event_handlers.on_notification_created_send import (
        on_notification_created_send,
    )
    from app.context.notification.domain.events.notification_events import NotificationCreated

    def _build_on_notification_created(session: AsyncSession) -> MessageHandlerFn:
        sender_port = container.notification_sender_port()

        async def _run(message: dict[str, Any]) -> None:
            # BrokerDomainEventBus оборачивает событие в envelope {event_type, event_id, occurred_at, payload}
            payload = message.get("payload", {})

            # Валидация обязательных полей — не используем fallback-дефолты для критичных полей
            notification_id = payload.get("notification_id")
            recipient_id = payload.get("recipient_id")
            notification_type_raw = payload.get("notification_type")

            if not notification_id or not recipient_id or not notification_type_raw:
                logger.error(
                    "NotificationCreated event missing required fields, skipping",
                    notification_id=notification_id,
                    recipient_id=recipient_id,
                    notification_type=notification_type_raw,
                )
                return

            try:
                # Enum'ы могут прийти как enum-объект, "task_assigned" (.value) или "NotificationType.TASK_ASSIGNED" (str(enum))
                if isinstance(notification_type_raw, NotificationType):
                    notification_type_raw = notification_type_raw.value
                else:
                    notification_type_raw = str(notification_type_raw)
                    if notification_type_raw.startswith("NotificationType."):
                        notification_type_raw = notification_type_raw.split(".", 1)[1]

                priority_raw_val = payload.get("priority", "normal")
                if isinstance(priority_raw_val, NotificationPriority):
                    priority_raw = priority_raw_val.value
                else:
                    priority_raw = str(priority_raw_val)
                    if priority_raw.startswith("NotificationPriority."):
                        priority_raw = priority_raw.split(".", 1)[1]

                channels_raw = payload.get("channels", ["in_app"])
                channels = []
                for ch in channels_raw:
                    if isinstance(ch, ChannelType):
                        channels.append(ch)
                    else:
                        ch_str = str(ch)
                        channels.append(ChannelType(ch_str.split(".", 1)[1] if "." in ch_str else ch_str))

                event = NotificationCreated(
                    notification_id=notification_id,
                    recipient_id=recipient_id,
                    notification_type=NotificationType(notification_type_raw),
                    title=payload.get("title", ""),
                    body=payload.get("body", ""),
                    priority=NotificationPriority(priority_raw),
                    channels=channels,
                )
            except (ValueError, KeyError) as e:
                logger.error("Failed to deserialize NotificationCreated event, skipping", error=str(e), message=message)
                return

            await on_notification_created_send(event, sender_port)

        return _run

    return [
        # Notification BC (self)
        Subscription(
            topic=NOTIFICATION_EVENTS_TOPIC,
            group_id="notification-bc--notification-created",
            build_handler=_build_on_notification_created,
        ),
        # Identity BC
        Subscription(
            topic=IDENTITY_EVENTS_TOPIC,
            group_id="notification-bc--user-registered",
            build_handler=_build_on_user_registered,
        ),
        Subscription(
            topic=IDENTITY_EVENTS_TOPIC,
            group_id="notification-bc--email-confirmed",
            build_handler=_build_on_email_confirmed,
        ),
        Subscription(
            topic=IDENTITY_EVENTS_TOPIC,
            group_id="notification-bc--password-changed",
            build_handler=_build_on_password_changed,
        ),
        Subscription(
            topic=IDENTITY_EVENTS_TOPIC,
            group_id="notification-bc--new-device-login",
            build_handler=_build_on_new_device_login,
        ),
        Subscription(
            topic=IDENTITY_EVENTS_TOPIC,
            group_id="notification-bc--auth-factor-changed",
            build_handler=_build_on_auth_factor_changed,
        ),
        Subscription(
            topic=IDENTITY_EVENTS_TOPIC,
            group_id="notification-bc--user-deleted",
            build_handler=_build_on_user_deleted,
        ),
        # Organization BC
        Subscription(
            topic=ORGANIZATION_EVENTS_TOPIC,
            group_id="notification-bc--org-invitation",
            build_handler=_build_on_org_invitation,
        ),
        # Workspace BC
        Subscription(
            topic=WORKSPACE_EVENTS_TOPIC,
            group_id="notification-bc--workspace-invitation",
            build_handler=_build_on_workspace_invitation,
        ),
        # Project BC
        Subscription(
            topic=PROJECT_EVENTS_TOPIC,
            group_id="notification-bc--project-member-joined",
            build_handler=_build_on_project_member_joined,
        ),
        Subscription(
            topic=PROJECT_EVENTS_TOPIC,
            group_id="notification-bc--sprint-started",
            build_handler=_build_on_sprint_started,
        ),
        Subscription(
            topic=PROJECT_EVENTS_TOPIC,
            group_id="notification-bc--sprint-completed",
            build_handler=_build_on_sprint_completed,
        ),
        Subscription(
            topic=PROJECT_EVENTS_TOPIC,
            group_id="notification-bc--project-deadline-approaching",
            build_handler=_build_on_project_deadline_approaching,
        ),
        Subscription(
            topic=PROJECT_EVENTS_TOPIC,
            group_id="notification-bc--project-overdue",
            build_handler=_build_on_project_overdue,
        ),
        # Task BC
        Subscription(
            topic=TASK_EVENTS_TOPIC,
            group_id="notification-bc--task-assigned",
            build_handler=_build_on_task_assigned,
        ),
        Subscription(
            topic=TASK_EVENTS_TOPIC,
            group_id="notification-bc--task-unassigned",
            build_handler=_build_on_task_unassigned,
        ),
        Subscription(
            topic=TASK_EVENTS_TOPIC,
            group_id="notification-bc--task-status-changed",
            build_handler=_build_on_task_status_changed,
        ),
        Subscription(
            topic=TASK_EVENTS_TOPIC,
            group_id="notification-bc--task-comment-added",
            build_handler=_build_on_task_comment_added,
        ),
        Subscription(
            topic=TASK_EVENTS_TOPIC,
            group_id="notification-bc--task-deadline-approaching",
            build_handler=_build_on_task_deadline_approaching,
        ),
        Subscription(
            topic=TASK_EVENTS_TOPIC,
            group_id="notification-bc--task-overdue",
            build_handler=_build_on_task_overdue,
        ),
        Subscription(
            topic=TASK_EVENTS_TOPIC,
            group_id="notification-bc--task-info-changed",
            build_handler=_build_on_task_info_changed,
        ),
    ]
