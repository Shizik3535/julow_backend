from __future__ import annotations

from typing import Any

from app.shared.domain.value_objects.id_vo import Id

from app.context.filestorage.domain.aggregates.folder import Folder
from app.context.filestorage.domain.repositories.folder_repository import FolderRepository


class OnProjectCreatedCreateFolder:
    """
    Обработчик события Project BC `ProjectCreated`.

    Автоматически создаёт папку проекта (FolderType.PROJECT)
    в FileStorage BC при создании нового проекта.
    """

    def __init__(self, folder_repo: FolderRepository) -> None:
        self._folder_repo = folder_repo

    async def handle(self, message: dict[str, Any]) -> None:
        event_type = message.get("event_type") or message.get("type")
        if event_type != "ProjectCreated":
            return

        payload = message.get("payload") or message
        project_id = payload.get("project_id")
        workspace_id = payload.get("workspace_id")
        # ProjectCreated не содержит owner_id; используем workspace_id как
        # системного владельца папки. Может быть переназначен явной командой.
        owner_id = payload.get("owner_id") or payload.get("created_by") or workspace_id
        name = payload.get("name") or "Project"
        if not project_id or not workspace_id:
            return

        existing = await self._folder_repo.get_by_project(Id.from_string(project_id))
        if existing is not None:
            return

        folder = Folder.create_project_folder(
            name=name,
            workspace_id=Id.from_string(workspace_id),
            project_id=Id.from_string(project_id),
            owner_id=Id.from_string(owner_id),
        )
        await self._folder_repo.add(folder)
