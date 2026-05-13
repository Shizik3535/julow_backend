from __future__ import annotations

import asyncio

from dependency_injector import containers, providers

from app.context.identity.application.messaging import (
    build_identity_event_bus,
    identity_subscriptions,
)
from app.context.communication.application.messaging import (
    build_communication_event_bus,
    communication_subscriptions,
)
from app.context.notification.application.messaging import (
    build_notification_event_bus,
    notification_subscriptions,
)
from app.context.organization.application.messaging import (
    build_organization_event_bus,
    organization_subscriptions,
)
from app.context.profile.application.messaging import (
    build_profile_event_bus,
    profile_subscriptions,
)
from app.context.workspace.application.messaging import (
    build_workspace_event_bus,
    workspace_subscriptions,
)
from app.context.project.application.messaging import (
    build_project_event_bus,
    project_subscriptions,
)
from app.context.task.application.messaging import (
    build_task_event_bus,
    task_subscriptions,
)
from app.context.timetracking.application.messaging import (
    build_timetracking_event_bus,
    timetracking_subscriptions,
)
from app.context.filestorage.application.messaging import (
    build_filestorage_event_bus,
    filestorage_subscriptions,
)
from app.core.config.settings import Settings
from app.core.di.providers.auth_provider import create_auth_token_adapter, create_password_adapter
from app.core.di.providers.background_tasks_provider import create_celery_app
from app.core.di.providers.cache_provider import create_cache_adapter, create_redis_client
from app.core.di.providers.database_provider import create_db_engine, create_db_session_factory
from app.core.di.providers.identity_provider import (
    create_failed_login_policy,
    create_identity_notification_adapter,
    create_identity_org_sso_adapter,
    create_oauth_adapter,
    create_permission_checker,
    create_permission_provider,
    create_role_mapper,
    create_role_provider,
    create_role_repository,
    create_session_mapper,
    create_session_repository,
    create_sso_adapter,
    create_totp_adapter,
    create_user_auth_mapper,
    create_user_auth_repository,
    create_user_mapper,
    create_user_provider,
    create_user_repository,
)
from app.core.di.providers.communication_provider import (
    create_chat_mapper,
    create_chat_repository,
    create_comment_mapper,
    create_comment_repository,
    create_comment_target_access_adapter,
    create_communication_file_attachment_adapter,
    create_conference_provider_registry,
    create_meeting_mapper,
    create_meeting_repository,
    create_message_mapper,
    create_message_repository,
)
from app.core.di.providers.notification_provider import (
    create_device_token_mapper,
    create_device_token_repository,
    create_identity_user_adapter,
    create_notification_mapper,
    create_notification_preferences_mapper,
    create_notification_preferences_provider_adapter,
    create_notification_preferences_repository,
    create_notification_repository,
    create_chat_members_adapter,
    create_chat_members_provider,
    create_notification_sender_adapter,
    create_project_member_adapter,
    create_reminder_window_provider_adapter,
    create_task_participant_adapter,
    create_websocket_adapter,
    create_websocket_manager,
)
from app.core.di.providers.messaging_provider import create_kafka_producer
from app.core.di.providers.organization_provider import (
    create_department_mapper,
    create_department_repository,
    create_fernet_encryption_adapter,
    create_invitation_mapper,
    create_invitation_repository,
    create_org_identity_user_adapter,
    create_org_membership_mapper,
    create_org_membership_repository,
    create_org_permission_checker,
    create_org_role_mapper,
    create_org_role_repository,
    create_organization_mapper,
    create_organization_membership_provider,
    create_organization_permission_provider,
    create_organization_provider,
    create_organization_repository,
    create_organization_sso_provider,
    create_sso_integration_mapper,
    create_sso_integration_repository,
    create_storage_integration_mapper,
    create_storage_integration_repository,
    create_team_mapper,
    create_team_repository,
)
from app.core.di.providers.profile_provider import (
    create_identity_user_adapter,
    create_organization_membership_adapter,
    create_profile_mapper,
    create_profile_repository,
    create_profile_settings_provider,
    create_profile_user_provider,
    create_start_page_registry_adapter,
)
from app.core.di.providers.notification_provider import create_email_adapter, create_push_adapter
from app.core.di.providers.storage_provider import create_s3_session, get_s3_client_kwargs
from app.core.di.providers.workspace_provider import (
    create_ws_identity_user_adapter,
    create_ws_org_permission_checker_adapter,
    create_ws_organization_adapter,
    create_ws_organization_membership_adapter,
    create_workspace_invitation_mapper,
    create_workspace_invitation_repository,
    create_workspace_mapper,
    create_workspace_membership_mapper,
    create_workspace_membership_provider_adapter,
    create_workspace_membership_repository,
    create_workspace_permission_checker,
    create_workspace_provider_adapter,
    create_workspace_repository,
    create_workspace_role_mapper,
    create_workspace_role_repository,
    create_workspace_team_mapper,
    create_workspace_team_repository,
)
from app.core.di.providers.project_provider import (
    create_board_mapper,
    create_board_provider_adapter,
    create_board_repository,
    create_epic_mapper,
    create_epic_provider_adapter,
    create_epic_repository,
    create_project_identity_user_adapter,
    create_project_mapper,
    create_project_membership_mapper,
    create_project_membership_provider_adapter,
    create_project_membership_repository,
    create_project_org_membership_adapter,
    create_project_permission_checker,
    create_project_permission_provider,
    create_project_provider_adapter,
    create_project_reminder_window_adapter,
    create_project_repository,
    create_project_role_mapper,
    create_project_role_provider_adapter,
    create_project_role_repository,
    create_project_workspace_adapter,
    create_project_workspace_membership_adapter,
    create_project_ws_permission_checker_adapter,
    create_retro_template_mapper,
    create_retro_template_repository,
    create_sprint_mapper,
    create_sprint_provider_adapter,
    create_sprint_repository,
)
from app.core.di.providers.filestorage_provider import (
    create_file_attachment_provider,
    create_file_mapper,
    create_file_repository,
    create_folder_mapper,
    create_folder_repository,
    create_fs_identity_user_adapter,
    create_fs_workspace_adapter,
    create_fs_workspace_permission_checker,
    create_storage_mapper,
    create_storage_repository,
)
from app.core.di.providers.task_provider import (
    create_changelog_mapper,
    create_changelog_repository,
    create_task_board_adapter,
    create_task_epic_adapter,
    create_task_file_attachment_adapter,
    create_task_identity_user_adapter,
    create_task_mapper,
    create_task_participant_provider_adapter,
    create_task_permission_checker,
    create_task_project_adapter,
    create_task_project_membership_adapter,
    create_task_provider_adapter,
    create_task_reminder_window_adapter,
    create_task_repository,
    create_task_sprint_adapter,
    create_task_template_mapper,
    create_task_template_repository,
)
from app.core.di.providers.timetracking_provider import (
    create_activity_category_mapper,
    create_activity_category_repository,
    create_time_entry_mapper,
    create_time_entry_repository,
    create_time_entry_tag_mapper,
    create_time_entry_tag_repository,
    create_timetracking_epic_adapter,
    create_timetracking_identity_user_adapter,
    create_timetracking_permission_checker,
    create_timetracking_project_adapter,
    create_timetracking_task_adapter,
    create_timetracking_workspace_adapter,
)
from app.shared.application.messaging.subscription import Subscription
from app.shared.application.messaging.uow_subscriber import subscribe_with_uow
from app.shared.infrastructure.background_tasks.celery_background_tasks_adapter import (
    CeleryBackgroundTasksAdapter,
)
from app.shared.infrastructure.file_storage.s3_file_storage_adapter import S3FileStorageAdapter
from app.shared.infrastructure.messaging.kafka_message_broker_adapter import KafkaMessageBrokerAdapter
from app.shared.infrastructure.security.clamav_scanner_adapter import ClamAvScannerAdapter
from app.shared.infrastructure.security.noop_scanner_adapter import NoOpScannerAdapter


def _create_virus_scanner(clamav_settings):  # noqa: ANN001
    """
    Factory: ``VirusScannerPort``.

    Если ClamAV отключён — возвращает ``NoOpScannerAdapter`` (для dev/test).
    Иначе — ``ClamAvScannerAdapter`` с настройками из env.
    """
    if not clamav_settings.enabled:
        return NoOpScannerAdapter()
    return ClamAvScannerAdapter(
        host=clamav_settings.host,
        port=clamav_settings.port,
        timeout_seconds=clamav_settings.timeout_seconds,
        chunk_size_bytes=clamav_settings.chunk_size_bytes,
    )


class Container(containers.DeclarativeContainer):
    """
    DI-контейнер — Composition Root приложения.

    Все зависимости собираются здесь. Контейнер создаётся один раз
    при старте приложения и передаётся через FastAPI state.

    Использование:
        container = Container()
        container.init_resources()
        container.wire(modules=[...])
    """

    wiring_config = containers.WiringConfiguration(
        modules=[],
        auto_wire=True,
    )

    # Settings
    settings = providers.Singleton(Settings)

    # Auth
    auth_token_port = providers.Singleton(
        create_auth_token_adapter,
        settings=settings.provided.auth,
    )
    password_port = providers.Factory(create_password_adapter)

    # Database
    db_engine = providers.Singleton(
        create_db_engine,
        settings=settings.provided.db,
    )
    db_session_factory = providers.Singleton(
        create_db_session_factory,
        engine=db_engine,
    )

    # Cache
    redis_client = providers.Singleton(
        create_redis_client,
        settings=settings.provided.redis,
    )
    cache_port = providers.Singleton(
        create_cache_adapter,
        redis_client=redis_client,
        key_prefix="julow",
    )

    # File Storage
    s3_session = providers.Singleton(create_s3_session)
    s3_client_kwargs = providers.Singleton(
        get_s3_client_kwargs,
        settings=settings.provided.s3,
    )
    file_storage_port = providers.Singleton(
        S3FileStorageAdapter,
        session=s3_session,
        client_kwargs=s3_client_kwargs,
        bucket_name=settings.provided.s3.bucket_name,
        public_url_base=settings.provided.s3.endpoint_url,
    )

    # Antivirus (ClamAV в production, NoOp в dev/test)
    virus_scanner_port = providers.Singleton(
        _create_virus_scanner,
        clamav_settings=settings.provided.clamav,
    )

    # Messaging
    kafka_producer = providers.Singleton(
        create_kafka_producer,
        settings=settings.provided.kafka,
    )
    message_broker_port = providers.Singleton(
        KafkaMessageBrokerAdapter,
        producer=kafka_producer,
        bootstrap_servers=settings.provided.kafka.bootstrap_servers,
        auto_offset_reset=settings.provided.kafka.auto_offset_reset,
    )

    # Notification
    email_port = providers.Singleton(
        create_email_adapter,
        settings=settings.provided.smtp,
    )
    push_port = providers.Singleton(
        create_push_adapter,
        settings=settings.provided.ntfy,
    )

    # Background Tasks
    celery_app = providers.Singleton(
        create_celery_app,
        settings=settings.provided.celery,
    )
    background_tasks_port = providers.Singleton(
        CeleryBackgroundTasksAdapter,
        celery_app=celery_app,
    )

    # Event Buses (Singleton per BC) — use case'ы публикуют в свою шину,
    # которая внутри использует message_broker_port.
    identity_event_bus = providers.Singleton(
        build_identity_event_bus,
        broker=message_broker_port,
    )
    profile_event_bus = providers.Singleton(
        build_profile_event_bus,
        broker=message_broker_port,
    )

    # Identity BC - Mappers (Singleton)
    user_mapper = providers.Singleton(create_user_mapper)
    user_auth_mapper = providers.Singleton(create_user_auth_mapper)
    session_mapper = providers.Singleton(create_session_mapper)
    role_mapper = providers.Singleton(create_role_mapper)

    # Identity BC - Repositories (Factory with session)
    user_repo = providers.Factory(
        create_user_repository,
        session=db_session_factory,
        mapper=user_mapper,
    )
    user_auth_repo = providers.Factory(
        create_user_auth_repository,
        session=db_session_factory,
        mapper=user_auth_mapper,
    )
    session_repo = providers.Factory(
        create_session_repository,
        session=db_session_factory,
        mapper=session_mapper,
    )
    role_repo = providers.Factory(
        create_role_repository,
        session=db_session_factory,
        mapper=role_mapper,
    )

    # Identity BC - Domain policies
    failed_login_policy = providers.Singleton(create_failed_login_policy)

    # Identity BC - Authorization
    permission_checker = providers.Factory(
        create_permission_checker,
        user_repo=user_repo,
        role_repo=role_repo,
    )
    identity_permission_provider = providers.Factory(
        create_permission_provider,
        permission_checker=permission_checker,
    )

    # Identity BC - Integration outboard adapters
    identity_user_provider = providers.Factory(
        create_user_provider,
        user_repo=user_repo,
    )
    identity_role_provider = providers.Factory(
        create_role_provider,
        role_repo=role_repo,
        user_repo=user_repo,
    )

    # Identity BC - BC-специфичные адаптеры
    totp_port = providers.Singleton(create_totp_adapter)
    oauth_port = providers.Singleton(
        create_oauth_adapter,
        client_id_map=providers.Dict(
            oauth_google=settings.provided.oauth.google_client_id,
            oauth_github=settings.provided.oauth.github_client_id,
        ),
        client_secret_map=providers.Dict(
            oauth_google=settings.provided.oauth.google_client_secret,
            oauth_github=settings.provided.oauth.github_client_secret,
        ),
    )
    identity_notification_port = providers.Singleton(
        create_identity_notification_adapter,
        email_port=email_port,
        frontend_base_url=settings.provided.app.api_prefix,
    )

    # Profile BC - Mappers (Singleton)
    profile_mapper = providers.Singleton(create_profile_mapper)

    # Profile BC - Repositories (Factory with session)
    profile_repo = providers.Factory(
        create_profile_repository,
        session=db_session_factory,
        mapper=profile_mapper,
    )

    # Profile BC - Integration inboard adapters
    profile_identity_user_port = providers.Factory(
        create_identity_user_adapter,
        identity_user_provider=identity_user_provider,
    )

    # Profile BC - Integration outboard adapters
    profile_user_provider = providers.Factory(
        create_profile_user_provider,
        profile_repo=profile_repo,
    )
    profile_settings_provider = providers.Factory(
        create_profile_settings_provider,
        profile_repo=profile_repo,
    )

    # Profile BC - BC-specific adapters (Singleton — без состояния)
    start_page_registry_port = providers.Singleton(create_start_page_registry_adapter)

    # Organization BC - Event Bus
    organization_event_bus = providers.Singleton(
        build_organization_event_bus,
        broker=message_broker_port,
    )

    # Organization BC - Mappers (Singleton)
    organization_mapper = providers.Singleton(create_organization_mapper)
    org_membership_mapper = providers.Singleton(create_org_membership_mapper)
    team_mapper = providers.Singleton(create_team_mapper)
    org_role_mapper = providers.Singleton(create_org_role_mapper)
    department_mapper = providers.Singleton(create_department_mapper)
    invitation_mapper = providers.Singleton(create_invitation_mapper)
    sso_integration_mapper = providers.Singleton(create_sso_integration_mapper)
    storage_integration_mapper = providers.Singleton(create_storage_integration_mapper)

    # Organization BC - Repositories (Factory with session)
    organization_repo = providers.Factory(
        create_organization_repository,
        session=db_session_factory,
        mapper=organization_mapper,
    )
    org_membership_repo = providers.Factory(
        create_org_membership_repository,
        session=db_session_factory,
        mapper=org_membership_mapper,
    )
    team_repo = providers.Factory(
        create_team_repository,
        session=db_session_factory,
        mapper=team_mapper,
    )
    org_role_repo = providers.Factory(
        create_org_role_repository,
        session=db_session_factory,
        mapper=org_role_mapper,
    )
    department_repo = providers.Factory(
        create_department_repository,
        session=db_session_factory,
        mapper=department_mapper,
    )
    invitation_repo = providers.Factory(
        create_invitation_repository,
        session=db_session_factory,
        mapper=invitation_mapper,
    )
    sso_integration_repo = providers.Factory(
        create_sso_integration_repository,
        session=db_session_factory,
        mapper=sso_integration_mapper,
    )
    storage_integration_repo = providers.Factory(
        create_storage_integration_repository,
        session=db_session_factory,
        mapper=storage_integration_mapper,
    )

    # Organization BC - Authorization
    org_permission_checker = providers.Factory(
        create_org_permission_checker,
        membership_repo=org_membership_repo,
        org_role_repo=org_role_repo,
    )

    # Organization BC - Outboard permission provider (для потребления другими BC)
    org_permission_provider = providers.Factory(
        create_organization_permission_provider,
        permission_checker=org_permission_checker,
    )

    # Organization BC - Integration inboard adapters
    org_identity_user_port = providers.Factory(
        create_org_identity_user_adapter,
        identity_user_provider=identity_user_provider,
    )

    # Organization BC - Integration outboard adapters
    org_provider = providers.Factory(
        create_organization_provider,
        repo=organization_repo,
    )
    org_membership_provider = providers.Factory(
        create_organization_membership_provider,
        repo=org_membership_repo,
        org_repo=organization_repo,
    )

    # Organization BC - BC-specific adapters
    encryption_port = providers.Singleton(
        create_fernet_encryption_adapter,
        encryption_key=settings.provided.encryption.key,
    )

    # Organization BC - SSO outboard provider
    org_sso_provider = providers.Factory(
        create_organization_sso_provider,
        sso_repo=sso_integration_repo,
        org_repo=organization_repo,
        encryption_port=encryption_port,
    )

    # Identity BC - SSO adapters
    sso_port = providers.Singleton(create_sso_adapter)

    # Identity BC - Organization SSO inboard port
    identity_org_sso_port = providers.Factory(
        create_identity_org_sso_adapter,
        org_sso_provider=org_sso_provider,
    )

    # Profile BC - Organization integration (real adapter via Organization outboard)
    organization_membership_port = providers.Factory(
        create_organization_membership_adapter,
        org_membership_provider=org_membership_provider,
    )

    # Workspace BC - Event Bus
    workspace_event_bus = providers.Singleton(
        build_workspace_event_bus,
        broker=message_broker_port,
    )

    # Workspace BC - Mappers (Singleton)
    workspace_mapper = providers.Singleton(create_workspace_mapper)
    workspace_membership_mapper = providers.Singleton(create_workspace_membership_mapper)
    workspace_role_mapper = providers.Singleton(create_workspace_role_mapper)
    workspace_team_mapper = providers.Singleton(create_workspace_team_mapper)
    workspace_invitation_mapper = providers.Singleton(create_workspace_invitation_mapper)

    # Workspace BC - Repositories (Factory with session)
    workspace_repo = providers.Factory(
        create_workspace_repository,
        session=db_session_factory,
        mapper=workspace_mapper,
    )
    workspace_membership_repo = providers.Factory(
        create_workspace_membership_repository,
        session=db_session_factory,
        mapper=workspace_membership_mapper,
    )
    workspace_role_repo = providers.Factory(
        create_workspace_role_repository,
        session=db_session_factory,
        mapper=workspace_role_mapper,
    )
    workspace_team_repo = providers.Factory(
        create_workspace_team_repository,
        session=db_session_factory,
        mapper=workspace_team_mapper,
    )
    workspace_invitation_repo = providers.Factory(
        create_workspace_invitation_repository,
        session=db_session_factory,
        mapper=workspace_invitation_mapper,
    )

    # Workspace BC - Integration inboard adapters
    ws_identity_user_port = providers.Factory(
        create_ws_identity_user_adapter,
        identity_user_provider=identity_user_provider,
    )
    ws_organization_membership_port = providers.Factory(
        create_ws_organization_membership_adapter,
        org_membership_provider=org_membership_provider,
    )
    ws_organization_port = providers.Factory(
        create_ws_organization_adapter,
        organization_provider=org_provider,
    )
    ws_org_permission_checker_port = providers.Factory(
        create_ws_org_permission_checker_adapter,
        org_permission_provider=org_permission_provider,
    )

    # Workspace BC - Integration outboard adapters
    workspace_provider = providers.Factory(
        create_workspace_provider_adapter,
        repo=workspace_repo,
    )
    workspace_membership_provider = providers.Factory(
        create_workspace_membership_provider_adapter,
        membership_repo=workspace_membership_repo,
        workspace_role_repo=workspace_role_repo,
        workspace_repo=workspace_repo,
    )

    # Workspace BC - Authorization
    workspace_permission_checker = providers.Factory(
        create_workspace_permission_checker,
        membership_repo=workspace_membership_repo,
        workspace_role_repo=workspace_role_repo,
        ws_repo=workspace_repo,
        org_permission_checker=ws_org_permission_checker_port,
    )

    # ==================================================================
    # Project BC
    # ==================================================================

    # Project BC - Event Bus
    project_event_bus = providers.Singleton(
        build_project_event_bus,
        broker=message_broker_port,
    )

    # Project BC - Mappers (Singleton)
    project_mapper = providers.Singleton(create_project_mapper)
    board_mapper = providers.Singleton(create_board_mapper)
    epic_mapper = providers.Singleton(create_epic_mapper)
    sprint_mapper = providers.Singleton(create_sprint_mapper)
    project_membership_mapper = providers.Singleton(create_project_membership_mapper)
    project_role_mapper = providers.Singleton(create_project_role_mapper)
    retro_template_mapper = providers.Singleton(create_retro_template_mapper)

    # Project BC - Repositories (Factory with session)
    project_repo = providers.Factory(
        create_project_repository,
        session=db_session_factory,
        mapper=project_mapper,
    )
    board_repo = providers.Factory(
        create_board_repository,
        session=db_session_factory,
        mapper=board_mapper,
    )
    epic_repo = providers.Factory(
        create_epic_repository,
        session=db_session_factory,
        mapper=epic_mapper,
    )
    sprint_repo = providers.Factory(
        create_sprint_repository,
        session=db_session_factory,
        mapper=sprint_mapper,
    )
    project_membership_repo = providers.Factory(
        create_project_membership_repository,
        session=db_session_factory,
        mapper=project_membership_mapper,
    )
    project_role_repo = providers.Factory(
        create_project_role_repository,
        session=db_session_factory,
        mapper=project_role_mapper,
    )
    retro_template_repo = providers.Factory(
        create_retro_template_repository,
        session=db_session_factory,
        mapper=retro_template_mapper,
    )

    # Project BC - Integration inboard adapters
    project_identity_user_port = providers.Factory(
        create_project_identity_user_adapter,
        identity_user_provider=identity_user_provider,
    )
    project_workspace_port = providers.Factory(
        create_project_workspace_adapter,
        workspace_provider=workspace_provider,
    )
    project_workspace_membership_port = providers.Factory(
        create_project_workspace_membership_adapter,
        workspace_membership_provider=workspace_membership_provider,
    )
    project_org_membership_port = providers.Factory(
        create_project_org_membership_adapter,
        org_membership_provider=org_membership_provider,
    )
    project_ws_permission_checker_port = providers.Factory(
        create_project_ws_permission_checker_adapter,
        workspace_membership_provider=workspace_membership_provider,
    )

    # Project BC - Integration outboard adapters
    project_provider = providers.Factory(
        create_project_provider_adapter,
        repo=project_repo,
    )
    board_provider = providers.Factory(
        create_board_provider_adapter,
        repo=board_repo,
    )
    epic_provider = providers.Factory(
        create_epic_provider_adapter,
        repo=epic_repo,
    )
    sprint_provider = providers.Factory(
        create_sprint_provider_adapter,
        repo=sprint_repo,
    )
    project_membership_provider = providers.Factory(
        create_project_membership_provider_adapter,
        repo=project_membership_repo,
    )
    project_role_provider = providers.Factory(
        create_project_role_provider_adapter,
        repo=project_role_repo,
    )

    # Project BC - Authorization
    project_permission_checker = providers.Factory(
        create_project_permission_checker,
        membership_repo=project_membership_repo,
        project_role_repo=project_role_repo,
        project_repo=project_repo,
        workspace_permission_checker=project_ws_permission_checker_port,
    )
    project_permission_provider = providers.Factory(
        create_project_permission_provider,
        checker=project_permission_checker,
    )
    # ==================================================================
    # Notification BC
    # ==================================================================

    # Notification BC - Event Bus
    notification_event_bus = providers.Singleton(
        build_notification_event_bus,
        broker=message_broker_port,
    )

    # Notification BC - Mappers (Singleton)
    notification_mapper = providers.Singleton(create_notification_mapper)
    notification_preferences_mapper = providers.Singleton(create_notification_preferences_mapper)
    device_token_mapper = providers.Singleton(create_device_token_mapper)

    # Notification BC - Repositories (Factory with session)
    notification_repo = providers.Factory(
        create_notification_repository,
        session=db_session_factory,
        mapper=notification_mapper,
    )
    notification_preferences_repo = providers.Factory(
        create_notification_preferences_repository,
        session=db_session_factory,
        mapper=notification_preferences_mapper,
    )
    device_token_repo = providers.Factory(
        create_device_token_repository,
        session=db_session_factory,
        mapper=device_token_mapper,
    )

    # Notification BC - WebSocket (Singleton)
    websocket_manager = providers.Singleton(create_websocket_manager)
    websocket_port = providers.Singleton(
        create_websocket_adapter,
        manager=websocket_manager,
    )

    # Notification BC - Integration Adapters (Factory)
    notification_identity_user_port = providers.Factory(
        create_identity_user_adapter,
        identity_user_provider=identity_user_provider,
    )
    notification_preferences_provider = providers.Factory(
        create_notification_preferences_provider_adapter,
        preferences_repo=notification_preferences_repo,
        session_factory=db_session_factory,
    )
    reminder_window_provider = providers.Factory(
        create_reminder_window_provider_adapter,
        preferences_repo=notification_preferences_repo,
        session_factory=db_session_factory,
    )

    # Reminder window adapters (depend on reminder_window_provider from Notification BC)
    project_reminder_window_port = providers.Factory(
        create_project_reminder_window_adapter,
        reminder_window_provider=reminder_window_provider,
    )
    task_reminder_window_port = providers.Factory(
        create_task_reminder_window_adapter,
        reminder_window_provider=reminder_window_provider,
    )

    # Notification BC - Notification Sender (Factory)
    notification_sender_port = providers.Factory(
        create_notification_sender_adapter,
        websocket_port=websocket_port,
        email_port=email_port,
        push_port=push_port,
        preferences_provider=notification_preferences_provider,
        identity_user_port=notification_identity_user_port,
    )

    # ==================================================================
    # Task BC
    # ==================================================================

    # Task BC - Event Bus
    task_event_bus = providers.Singleton(
        build_task_event_bus,
        broker=message_broker_port,
    )

    # Task BC - Mappers (Singleton)
    task_mapper = providers.Singleton(create_task_mapper)
    task_template_mapper = providers.Singleton(create_task_template_mapper)
    changelog_mapper = providers.Singleton(create_changelog_mapper)

    # Task BC - Repositories (Factory with session)
    task_repo = providers.Factory(
        create_task_repository,
        session=db_session_factory,
        mapper=task_mapper,
    )
    task_template_repo = providers.Factory(
        create_task_template_repository,
        session=db_session_factory,
        mapper=task_template_mapper,
    )
    changelog_repo = providers.Factory(
        create_changelog_repository,
        session=db_session_factory,
        mapper=changelog_mapper,
    )

    # Task BC - Integration outboard adapters
    task_provider = providers.Factory(
        create_task_provider_adapter,
        repo=task_repo,
    )
    task_participant_provider = providers.Factory(
        create_task_participant_provider_adapter,
        repo=task_repo,
    )

    # Task BC - Integration inboard adapters
    task_identity_user_port = providers.Factory(
        create_task_identity_user_adapter,
        identity_user_provider=identity_user_provider,
    )
    task_project_port = providers.Factory(
        create_task_project_adapter,
        project_provider=project_provider,
    )
    task_project_membership_port = providers.Factory(
        create_task_project_membership_adapter,
        project_membership_provider=project_membership_provider,
    )
    task_board_port = providers.Factory(
        create_task_board_adapter,
        board_provider=board_provider,
    )
    task_sprint_port = providers.Factory(
        create_task_sprint_adapter,
        sprint_provider=sprint_provider,
    )
    task_epic_port = providers.Factory(
        create_task_epic_adapter,
        epic_provider=epic_provider,
    )
    task_permission_checker_port = providers.Factory(
        create_task_permission_checker,
        task_repo=task_repo,
        project_membership_port=task_project_membership_port,
        project_permission_provider=project_permission_provider,
    )

    # ==================================================================
    # TimeTracking BC
    # ==================================================================

    # TimeTracking BC - Event Bus
    timetracking_event_bus = providers.Singleton(
        build_timetracking_event_bus,
        broker=message_broker_port,
    )

    # TimeTracking BC - Mappers (Singleton)
    time_entry_mapper = providers.Singleton(create_time_entry_mapper)
    activity_category_mapper = providers.Singleton(create_activity_category_mapper)
    time_entry_tag_mapper = providers.Singleton(create_time_entry_tag_mapper)

    # TimeTracking BC - Repositories (Factory with session)
    time_entry_repo = providers.Factory(
        create_time_entry_repository,
        session=db_session_factory,
        mapper=time_entry_mapper,
    )
    activity_category_repo = providers.Factory(
        create_activity_category_repository,
        session=db_session_factory,
        mapper=activity_category_mapper,
    )
    time_entry_tag_repo = providers.Factory(
        create_time_entry_tag_repository,
        session=db_session_factory,
        mapper=time_entry_tag_mapper,
    )

    # TimeTracking BC - Authorization
    timetracking_permission_checker_port = providers.Factory(
        create_timetracking_permission_checker,
        workspace_membership_provider=workspace_membership_provider,
    )

    # TimeTracking BC - Integration inboard adapters
    timetracking_workspace_port = providers.Factory(
        create_timetracking_workspace_adapter,
        workspace_provider=workspace_provider,
        workspace_membership_provider=workspace_membership_provider,
    )
    timetracking_task_port = providers.Factory(
        create_timetracking_task_adapter,
        task_provider=task_provider,
    )
    timetracking_project_port = providers.Factory(
        create_timetracking_project_adapter,
        project_provider=project_provider,
    )
    timetracking_epic_port = providers.Factory(
        create_timetracking_epic_adapter,
        epic_provider=epic_provider,
    )
    timetracking_identity_user_port = providers.Factory(
        create_timetracking_identity_user_adapter,
        identity_user_provider=identity_user_provider,
    )

    # ==================================================================
    # Communication BC
    # ==================================================================

    # Communication BC - Event Bus
    communication_event_bus = providers.Singleton(
        build_communication_event_bus,
        broker=message_broker_port,
    )

    # Communication BC - Mappers (Singleton)
    comment_mapper = providers.Singleton(create_comment_mapper)
    chat_mapper = providers.Singleton(create_chat_mapper)
    message_mapper = providers.Singleton(create_message_mapper)
    meeting_mapper = providers.Singleton(create_meeting_mapper)

    # Communication BC - Repositories (Factory with session)
    comment_repo = providers.Factory(
        create_comment_repository,
        session=db_session_factory,
        mapper=comment_mapper,
    )
    chat_repo = providers.Factory(
        create_chat_repository,
        session=db_session_factory,
        mapper=chat_mapper,
    )
    message_repo = providers.Factory(
        create_message_repository,
        session=db_session_factory,
        mapper=message_mapper,
    )
    meeting_repo = providers.Factory(
        create_meeting_repository,
        session=db_session_factory,
        mapper=meeting_mapper,
    )

    # Communication BC - Conference provider registry (Singleton)
    conference_provider_registry = providers.Singleton(
        create_conference_provider_registry,
    )

    # Communication BC - Integration inboard adapters
    comment_target_access_port = providers.Factory(
        create_comment_target_access_adapter,
        task_provider=task_provider,
        epic_provider=epic_provider,
        sprint_provider=sprint_provider,
        project_permission_provider=project_permission_provider,
    )

    # Communication BC - Outboard provider (chat members), exposed to Notification BC
    chat_members_provider = providers.Factory(
        create_chat_members_provider,
        repo=chat_repo,
    )

    # ==================================================================
    # FileStorage BC
    # ==================================================================

    # FileStorage BC - Event Bus
    filestorage_event_bus = providers.Singleton(
        build_filestorage_event_bus,
        broker=message_broker_port,
    )

    # FileStorage BC - Mappers (Singleton)
    file_mapper = providers.Singleton(create_file_mapper)
    folder_mapper = providers.Singleton(create_folder_mapper)
    storage_mapper = providers.Singleton(create_storage_mapper)

    # FileStorage BC - Repositories (Factory with session)
    file_repo = providers.Factory(
        create_file_repository,
        session=db_session_factory,
        mapper=file_mapper,
    )
    folder_repo = providers.Factory(
        create_folder_repository,
        session=db_session_factory,
        mapper=folder_mapper,
    )
    storage_repo = providers.Factory(
        create_storage_repository,
        session=db_session_factory,
        mapper=storage_mapper,
    )

    # FileStorage BC - Integration inboard adapters
    fs_workspace_permission_checker_port = providers.Factory(
        create_fs_workspace_permission_checker,
    )
    fs_identity_user_port = providers.Factory(
        create_fs_identity_user_adapter,
    )
    fs_workspace_port = providers.Factory(
        create_fs_workspace_adapter,
    )

    # FileStorage BC - Outboard provider (для Task/Communication BC)
    file_attachment_provider = providers.Factory(
        create_file_attachment_provider,
        file_repo=file_repo,
        storage_repo=storage_repo,
        file_storage=file_storage_port,
        event_bus=filestorage_event_bus,
    )

    # Task BC - inboard FileAttachmentAdapter (delegates to FileStorage BC)
    task_file_attachment_port = providers.Factory(
        create_task_file_attachment_adapter,
        file_attachment_provider=file_attachment_provider,
    )

    # Communication BC - inboard FileAttachmentAdapter
    communication_file_attachment_port = providers.Factory(
        create_communication_file_attachment_adapter,
        file_attachment_provider=file_attachment_provider,
    )

    # Notification BC - Integration Adapters that depend on Task/Project/Communication BC providers
    notification_task_participant_port = providers.Factory(
        create_task_participant_adapter,
        task_participant_provider=task_participant_provider,
    )
    notification_chat_members_port = providers.Factory(
        create_chat_members_adapter,
        chat_members_provider=chat_members_provider,
    )
    notification_project_member_port = providers.Factory(
        create_project_member_adapter,
        project_membership_provider=project_membership_provider,
        project_provider=project_provider,
    )


# ------------------------------------------------------------------
# Messaging wiring — см. wire_messaging() ниже.
# Каждый BC сам декларирует свои подписки в модуле
# app/context/<bc>/application/messaging.py
# ------------------------------------------------------------------


async def wire_messaging(container: Container) -> None:
    """
    Подписывает все BC на Kafka-топики через MessageBrokerPort.

    Сборщик подписок: каждый BC экспортирует функцию
    ``<bc>_subscriptions(container) -> list[Subscription]``. Здесь
    они просто коллекционируются и прокидываются в ``subscribe_with_uow``,
    который оборачивает каждое сообщение в собственную AsyncSession
    с commit/rollback.

    Публикация событий не требует wiring'а — use case'ы получают
    DomainEventBus через DI и публикуют напрямую.
    """
    broker = container.message_broker_port()
    session_factory = container.db_session_factory()

    subscriptions: list[Subscription] = [
        *identity_subscriptions(container),
        *profile_subscriptions(container),
        *organization_subscriptions(container),
        *workspace_subscriptions(container),
        *project_subscriptions(container),
        *task_subscriptions(container),
        *timetracking_subscriptions(container),
        *notification_subscriptions(container),
        *communication_subscriptions(container),
        *filestorage_subscriptions(container),
    ]

    await asyncio.gather(
        *(subscribe_with_uow(broker, session_factory, sub) for sub in subscriptions)
    )
