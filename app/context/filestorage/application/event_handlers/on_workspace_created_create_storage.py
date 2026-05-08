from __future__ import annotations

from typing import Any

from app.shared.domain.value_objects.id_vo import Id

from app.context.filestorage.domain.aggregates.storage import Storage
from app.context.filestorage.domain.repositories.storage_repository import StorageRepository
from app.context.filestorage.domain.value_objects.storage_config import StorageConfig
from app.context.filestorage.domain.value_objects.storage_owner_type import StorageOwnerType
from app.context.filestorage.domain.value_objects.storage_provider import StorageProvider


# Дефолт квоты workspace — 10 GB. Может быть пересмотрен через политику.
DEFAULT_WORKSPACE_MAX_BYTES = 10 * 1024 * 1024 * 1024


class OnWorkspaceCreatedCreateStorage:
    """
    Обработчик события Workspace BC `WorkspaceCreated`.

    Автоматически создаёт дефолтное хранилище (provider=LOCAL)
    для нового workspace, если оно ещё не существует.
    """

    def __init__(self, storage_repo: StorageRepository) -> None:
        self._storage_repo = storage_repo

    async def handle(self, message: dict[str, Any]) -> None:
        event_type = message.get("event_type") or message.get("type")
        if event_type != "WorkspaceCreated":
            return

        payload = message.get("payload") or message
        workspace_id = payload.get("workspace_id") or payload.get("ws_id")
        if not workspace_id:
            return

        owner_id_str = workspace_id
        existing = await self._storage_repo.get_by_owner(
            owner_type=StorageOwnerType.WORKSPACE,
            owner_id=Id.from_string(owner_id_str),
        )
        if existing is not None:
            return

        storage = Storage.create(
            owner_type=StorageOwnerType.WORKSPACE,
            owner_id=Id.from_string(workspace_id),
            provider=StorageProvider.LOCAL,
            config=StorageConfig(),
            max_bytes=DEFAULT_WORKSPACE_MAX_BYTES,
        )
        await self._storage_repo.add(storage)
