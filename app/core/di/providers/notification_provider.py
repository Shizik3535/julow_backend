"""DI providers для Notification BC."""
from __future__ import annotations

import httpx

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.context.notification.domain.repositories.notification_preferences_repository import (
    NotificationPreferencesRepository,
)
from app.context.notification.domain.repositories.notification_repository import NotificationRepository
from app.context.notification.domain.repositories.device_token_repository import DeviceTokenRepository
from app.context.notification.infrastructure.persistence.mappers.notification_mapper import NotificationMapper
from app.context.notification.infrastructure.persistence.mappers.notification_preferences_mapper import (
    NotificationPreferencesMapper,
)
from app.context.notification.infrastructure.persistence.mappers.device_token_mapper import DeviceTokenMapper
from app.context.notification.infrastructure.persistence.repositories.sql_notification_preferences_repository import (
    SqlNotificationPreferencesRepository,
)
from app.context.notification.infrastructure.persistence.repositories.sql_notification_repository import (
    SqlNotificationRepository,
)
from app.context.notification.infrastructure.persistence.repositories.sql_device_token_repository import (
    SqlDeviceTokenRepository,
)
from app.context.notification.infrastructure.notification.notification_sender_adapter import (
    NotificationSenderAdapter,
)
from app.context.notification.infrastructure.integration.inboard.identity_user_adapter import (
    IdentityUserAdapter,
)
from app.context.notification.infrastructure.integration.inboard.task_participant_adapter import (
    TaskParticipantAdapter,
)
from app.context.notification.infrastructure.integration.inboard.chat_members_adapter import (
    ChatMembersAdapter,
)
from app.context.notification.infrastructure.integration.inboard.project_member_adapter import (
    ProjectMemberAdapter,
)
from app.context.notification.infrastructure.integration.outboard.notification_preferences_provider_adapter import (
    NotificationPreferencesProviderAdapter,
)
from app.context.notification.infrastructure.integration.outboard.reminder_window_provider_adapter import (
    ReminderWindowProviderAdapter,
)
from app.context.notification.application.ports.notification.notification_sender_port import (
    NotificationSenderPort,
)
from app.context.notification.application.ports.integration.inboard.identity_user_port import (
    IdentityUserPort,
)
from app.context.notification.application.ports.integration.inboard.chat_members_port import (
    ChatMembersPort,
)
from app.context.notification.application.ports.integration.inboard.task_participant_port import (
    TaskParticipantPort,
)
from app.context.notification.application.ports.integration.inboard.project_member_port import (
    ProjectMemberPort,
)
from app.context.notification.application.ports.integration.outboard.notification_preferences_provider import (
    NotificationPreferencesProvider,
)
from app.context.notification.application.ports.integration.outboard.reminder_window_provider import (
    ReminderWindowProvider,
)
from app.context.identity.application.ports.integration.outboard.identity_user_provider import (
    IdentityUserProvider,
)
from app.context.communication.application.ports.integration.outboard.chat_members_provider import (
    ChatMembersProvider,
)
from app.context.task.application.ports.integration.outboard.task_participant_provider import (
    TaskParticipantProvider,
)
from app.context.project.application.ports.integration.outboard.project_membership_provider import (
    ProjectMembershipProvider,
)
from app.context.project.application.ports.integration.outboard.project_provider import (
    ProjectProvider,
)
from app.shared.application.ports.notification.email_port import EmailPort
from app.shared.application.ports.notification.push_port import PushPort
from app.shared.application.ports.notification.websocket_port import WebSocketPort
from app.shared.infrastructure.notification.smtp_email_adapter import SmtpEmailAdapter
from app.shared.infrastructure.notification.ntfy_push_adapter import NtfyPushAdapter
from app.shared.infrastructure.notification.websocket_adapter import WebSocketAdapter
from app.shared.infrastructure.notification.websocket_manager import WebSocketManager
from app.core.config.smtp_settings import SmtpSettings
from app.core.config.ntfy_settings import NtfySettings


# --- Email / Push Adapters ---


def create_email_adapter(settings: SmtpSettings) -> EmailPort:
    """Создать SmtpEmailAdapter."""
    return SmtpEmailAdapter(
        host=settings.host,
        port=settings.port,
        username=settings.username or None,
        password=settings.password or None,
        use_tls=settings.use_tls,
        from_email=settings.from_email,
    )


def create_push_adapter(settings: NtfySettings) -> PushPort:
    """Создать NtfyPushAdapter."""
    http_client = httpx.AsyncClient()
    return NtfyPushAdapter(
        base_url=settings.base_url,
        http_client=http_client,
    )


# --- Mappers ---


def create_notification_mapper() -> NotificationMapper:
    """Создать NotificationMapper."""
    return NotificationMapper()


def create_notification_preferences_mapper() -> NotificationPreferencesMapper:
    """Создать NotificationPreferencesMapper."""
    return NotificationPreferencesMapper()


def create_device_token_mapper() -> DeviceTokenMapper:
    """Создать DeviceTokenMapper."""
    return DeviceTokenMapper()


# --- Repositories ---


def create_notification_repository(
    session: AsyncSession,
    mapper: NotificationMapper,
) -> NotificationRepository:
    """Создать SqlNotificationRepository."""
    return SqlNotificationRepository(session=session, mapper=mapper)


def create_notification_preferences_repository(
    session: AsyncSession,
    mapper: NotificationPreferencesMapper,
) -> NotificationPreferencesRepository:
    """Создать SqlNotificationPreferencesRepository."""
    return SqlNotificationPreferencesRepository(session=session, mapper=mapper)


def create_device_token_repository(
    session: AsyncSession,
    mapper: DeviceTokenMapper,
) -> DeviceTokenRepository:
    """Создать SqlDeviceTokenRepository."""
    return SqlDeviceTokenRepository(session=session, mapper=mapper)


# --- WebSocket ---


def create_websocket_manager() -> WebSocketManager:
    """Создать WebSocketManager."""
    return WebSocketManager()


def create_websocket_adapter(manager: WebSocketManager) -> WebSocketPort:
    """Создать WebSocketAdapter."""
    return WebSocketAdapter(manager=manager)


# --- Notification Sender ---


def create_notification_sender_adapter(
    websocket_port: WebSocketPort,
    email_port: EmailPort,
    push_port: PushPort,
    preferences_provider: NotificationPreferencesProvider,
    identity_user_port: IdentityUserPort,
) -> NotificationSenderPort:
    """Создать NotificationSenderAdapter."""
    return NotificationSenderAdapter(
        websocket_port=websocket_port,
        email_port=email_port,
        push_port=push_port,
        preferences_provider=preferences_provider,
        identity_user_port=identity_user_port,
    )


# --- Integration Adapters ---


def create_identity_user_adapter(
    identity_user_provider: IdentityUserProvider,
) -> IdentityUserPort:
    """Создать IdentityUserAdapter."""
    return IdentityUserAdapter(identity_user_provider=identity_user_provider)


def create_task_participant_adapter(
    task_participant_provider: TaskParticipantProvider,
) -> TaskParticipantPort:
    """Создать TaskParticipantAdapter."""
    return TaskParticipantAdapter(task_participant_provider=task_participant_provider)


def create_chat_members_adapter(
    chat_members_provider: ChatMembersProvider,
) -> ChatMembersPort:
    """Создать ChatMembersAdapter для Notification BC."""
    return ChatMembersAdapter(chat_members_provider=chat_members_provider)


def create_chat_members_provider(
    repo,
) -> ChatMembersProvider:
    """Создать ChatMembersProviderAdapter (outboard Communication BC)."""
    from app.context.communication.infrastructure.integration.outboard.chat_members_provider_adapter import (
        ChatMembersProviderAdapter,
    )

    return ChatMembersProviderAdapter(repo=repo)


def create_project_member_adapter(
    project_membership_provider: ProjectMembershipProvider,
    project_provider: ProjectProvider,
) -> ProjectMemberPort:
    """Создать ProjectMemberAdapter."""
    return ProjectMemberAdapter(
        project_membership_provider=project_membership_provider,
        project_provider=project_provider,
    )


def create_notification_preferences_provider_adapter(
    preferences_repo: NotificationPreferencesRepository,
    session_factory: async_sessionmaker[AsyncSession] | None = None,
) -> NotificationPreferencesProvider:
    """Создать NotificationPreferencesProviderAdapter."""
    return NotificationPreferencesProviderAdapter(repo=preferences_repo, session_factory=session_factory)


def create_reminder_window_provider_adapter(
    preferences_repo: NotificationPreferencesRepository,
    session_factory: async_sessionmaker[AsyncSession] | None = None,
) -> ReminderWindowProvider:
    """Создать ReminderWindowProviderAdapter."""
    return ReminderWindowProviderAdapter(repo=preferences_repo, session_factory=session_factory)
