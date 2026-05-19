"""DI providers для FileStorage BC."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.ports.file_storage.file_storage_port import FileStoragePort

from app.context.filestorage.application.ports.integration.inboard.identity_user_port import (
    IdentityUserPort,
)
from app.context.filestorage.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.filestorage.application.ports.integration.inboard.workspace_port import (
    WorkspacePort,
)
from app.context.filestorage.application.ports.integration.outboard.file_attachment_provider import (
    FileAttachmentProvider,
)
from app.context.filestorage.domain.repositories.file_repository import FileRepository
from app.context.filestorage.domain.repositories.folder_repository import FolderRepository
from app.context.filestorage.domain.repositories.storage_repository import StorageRepository
from app.context.filestorage.infrastructure.integration.inboard.identity_user_adapter import (
    IdentityUserAdapter,
)
from app.context.filestorage.infrastructure.integration.inboard.workspace_adapter import (
    WorkspaceAdapter,
)
from app.context.filestorage.infrastructure.integration.inboard.workspace_permission_checker_adapter import (
    WorkspacePermissionCheckerAdapter,
)
from app.context.filestorage.infrastructure.integration.outboard.file_attachment_provider_adapter import (
    FileAttachmentProviderAdapter,
)
from app.context.filestorage.infrastructure.persistence.mappers.file_mapper import FileMapper
from app.context.filestorage.infrastructure.persistence.mappers.folder_mapper import FolderMapper
from app.context.filestorage.infrastructure.persistence.mappers.storage_mapper import StorageMapper
from app.context.filestorage.infrastructure.persistence.repositories.sql_file_repository import (
    SqlFileRepository,
)
from app.context.filestorage.infrastructure.persistence.repositories.sql_folder_repository import (
    SqlFolderRepository,
)
from app.context.filestorage.infrastructure.persistence.repositories.sql_storage_repository import (
    SqlStorageRepository,
)
from app.context.identity.application.ports.integration.outboard.identity_user_provider import (
    IdentityUserProvider,
)
from app.context.workspace.application.ports.integration.outboard.workspace_membership_provider import (
    WorkspaceMembershipProvider,
)
from app.context.workspace.application.ports.integration.outboard.workspace_provider import (
    WorkspaceProvider,
)


# --- Mappers ---


def create_file_mapper() -> FileMapper:
    """Создать FileMapper."""
    return FileMapper()


def create_folder_mapper() -> FolderMapper:
    """Создать FolderMapper."""
    return FolderMapper()


def create_storage_mapper() -> StorageMapper:
    """Создать StorageMapper."""
    return StorageMapper()


# --- Repositories ---


def create_file_repository(session: AsyncSession, mapper: FileMapper) -> FileRepository:
    """Создать SqlFileRepository."""
    return SqlFileRepository(session=session, mapper=mapper)


def create_folder_repository(session: AsyncSession, mapper: FolderMapper) -> FolderRepository:
    """Создать SqlFolderRepository."""
    return SqlFolderRepository(session=session, mapper=mapper)


def create_storage_repository(
    session: AsyncSession, mapper: StorageMapper
) -> StorageRepository:
    """Создать SqlStorageRepository."""
    return SqlStorageRepository(session=session, mapper=mapper)


# --- Integration adapters ---


def create_fs_workspace_permission_checker(
    workspace_membership_provider: WorkspaceMembershipProvider,
    project_membership_checker=None,
) -> WorkspacePermissionCheckerPort:
    """Создать WorkspacePermissionCheckerAdapter для FileStorage BC."""
    return WorkspacePermissionCheckerAdapter(
        workspace_membership_provider=workspace_membership_provider,
        project_membership_checker=project_membership_checker,
    )


def create_fs_identity_user_adapter(
    identity_user_provider: IdentityUserProvider,
) -> IdentityUserPort:
    """Создать IdentityUserAdapter для FileStorage BC."""
    return IdentityUserAdapter(identity_user_provider=identity_user_provider)


def create_fs_workspace_adapter(
    workspace_provider: WorkspaceProvider,
) -> WorkspacePort:
    """Создать WorkspaceAdapter для FileStorage BC."""
    return WorkspaceAdapter(workspace_provider=workspace_provider)


# --- Outboard: FileAttachmentProvider ---


def create_file_attachment_provider(
    file_repo: FileRepository,
    storage_repo: StorageRepository,
    file_storage: FileStoragePort,
    event_bus: DomainEventBus,
) -> FileAttachmentProvider:
    """
    Создать FileAttachmentProviderAdapter.

    Используется Task BC, Communication BC и др. для делегирования
    загрузки файлов-вложений в FileStorage BC (создание агрегата File,
    учёт квоты, события).
    """
    return FileAttachmentProviderAdapter(
        file_repo=file_repo,
        storage_repo=storage_repo,
        file_storage=file_storage,
        event_bus=event_bus,
    )
