import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.core.config import settings
from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel

# ORM models — импорт необходим, чтобы Alembic увидел таблицы в metadata
from app.context.identity.infrastructure.persistence.orm_models.user_orm import UserORM  # noqa: F401
from app.context.identity.infrastructure.persistence.orm_models.user_auth_orm import UserAuthORM  # noqa: F401
from app.context.identity.infrastructure.persistence.orm_models.session_orm import SessionORM  # noqa: F401
from app.context.identity.infrastructure.persistence.orm_models.role_orm import RoleORM  # noqa: F401
from app.context.profile.infrastructure.persistence.orm_models.user_profile_orm import (  # noqa: F401
    HotkeyConfigORM,
    NotificationPreferenceORM,
    PinnedItemORM,
    SidebarSectionORM,
    SocialLinkORM,
    UserProfileORM,
)
from app.context.organization.infrastructure.persistence.orm_models.organization_orm import (  # noqa: F401
    OrganizationORM,
    org_owners_table,
)
from app.context.organization.infrastructure.persistence.orm_models.org_membership_orm import (  # noqa: F401
    OrgMemberORM,
    OrgMembershipORM,
)
from app.context.organization.infrastructure.persistence.orm_models.team_orm import (  # noqa: F401
    TeamORM,
    team_members_table,
)
from app.context.organization.infrastructure.persistence.orm_models.org_role_orm import OrgRoleORM  # noqa: F401
from app.context.organization.infrastructure.persistence.orm_models.department_orm import (  # noqa: F401
    DepartmentORM,
    department_members_table,
)
from app.context.organization.infrastructure.persistence.orm_models.invitation_orm import InvitationORM  # noqa: F401
from app.context.organization.infrastructure.persistence.orm_models.sso_integration_orm import SSOIntegrationORM  # noqa: F401
from app.context.organization.infrastructure.persistence.orm_models.storage_integration_orm import StorageIntegrationORM  # noqa: F401
from app.context.workspace.infrastructure.persistence.orm_models.workspace_orm import WorkspaceORM  # noqa: F401
from app.context.workspace.infrastructure.persistence.orm_models.workspace_membership_orm import (  # noqa: F401
    WorkspaceMemberORM,
    WorkspaceMembershipORM,
)
from app.context.workspace.infrastructure.persistence.orm_models.workspace_role_orm import WorkspaceRoleORM  # noqa: F401
from app.context.workspace.infrastructure.persistence.orm_models.workspace_team_orm import WorkspaceTeamORM  # noqa: F401
from app.context.workspace.infrastructure.persistence.orm_models.workspace_invitation_orm import WorkspaceInvitationORM  # noqa: F401

# Alembic Config object
config = context.config

# Override sqlalchemy.url from app settings
config.set_main_option("sqlalchemy.url", settings.db.url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData for autogenerate support
target_metadata = BaseORMModel.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    SQL-скрипты генерируются без подключения к БД.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Настроить контекст и запустить миграции (sync)."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Run migrations in 'online' mode with async engine.

    Создаёт async SQLAlchemy engine, получает синхронное
    подключение через run_sync и выполняет миграции.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Точка входа для online-миграций (async)."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
