from __future__ import annotations

from dependency_injector import containers, providers

from app.context.identity.application.messaging import (
    build_identity_event_bus,
    identity_subscriptions,
)
from app.context.organization.application.messaging import (
    build_organization_event_bus,
    organization_subscriptions,
)
from app.context.profile.application.messaging import (
    build_profile_event_bus,
    profile_subscriptions,
)
from app.core.config.settings import Settings
from app.core.di.providers.auth_provider import create_auth_token_adapter, create_password_adapter
from app.core.di.providers.background_tasks_provider import create_celery_app
from app.core.di.providers.cache_provider import create_cache_adapter, create_redis_client
from app.core.di.providers.database_provider import create_db_engine, create_db_session_factory
from app.core.di.providers.identity_provider import (
    create_failed_login_policy,
    create_identity_notification_adapter,
    create_oauth_adapter,
    create_permission_checker,
    create_permission_provider,
    create_role_mapper,
    create_role_provider,
    create_role_repository,
    create_session_mapper,
    create_session_repository,
    create_totp_adapter,
    create_user_auth_mapper,
    create_user_auth_repository,
    create_user_mapper,
    create_user_provider,
    create_user_repository,
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
from app.shared.application.messaging.subscription import Subscription
from app.shared.application.messaging.uow_subscriber import subscribe_with_uow
from app.shared.infrastructure.background_tasks.celery_background_tasks_adapter import (
    CeleryBackgroundTasksAdapter,
)
from app.shared.infrastructure.file_storage.s3_file_storage_adapter import S3FileStorageAdapter
from app.shared.infrastructure.messaging.kafka_message_broker_adapter import KafkaMessageBrokerAdapter


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
    password_port = providers.Singleton(create_password_adapter)

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
    )

    # Organization BC - BC-specific adapters
    encryption_port = providers.Singleton(
        create_fernet_encryption_adapter,
        encryption_key=settings.provided.encryption.key,
    )

    # Profile BC - Organization integration (real adapter via Organization outboard)
    organization_membership_port = providers.Factory(
        create_organization_membership_adapter,
        org_membership_provider=org_membership_provider,
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
    ]

    for sub in subscriptions:
        await subscribe_with_uow(broker, session_factory, sub)
