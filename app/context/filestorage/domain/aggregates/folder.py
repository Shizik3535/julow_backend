from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.color_vo import Color
from app.context.filestorage.domain.value_objects.folder_type import FolderType
from app.context.filestorage.domain.value_objects.file_access_level import FileAccessLevel
from app.context.filestorage.domain.entities.file_permission_entry import FilePermissionEntry
from app.context.filestorage.domain.events.folder_events import (
    FolderCreated,
    FolderUpdated,
    FolderDeleted,
    FolderMoved,
)


@dataclass
class Folder(AggregateRoot):
    """
    Корень агрегата папки (FileStorage BC).

    Атрибуты:
        name: Название папки.
        folder_type: Тип папки.
        parent_folder_id: ID родительской папки (None = корень).
        color: Цвет (из shared kernel).
        description: Описание.
        icon: Иконка.
        owner_id: ID владельца.
        workspace_id: Opaque ID workspace.
        project_id: Opaque ID проекта (для PROJECT).
        is_pinned: Закреплена ли.
        is_shared: Расшарена ли.
        permissions: Список разрешений.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    name: str = ""
    folder_type: FolderType = FolderType.REGULAR
    parent_folder_id: Id | None = None
    color: Color | None = None
    description: str | None = None
    icon: str | None = None
    owner_id: Id = field(default_factory=Id.generate)
    workspace_id: Id = field(default_factory=Id.generate)
    project_id: Id | None = None
    is_pinned: bool = False
    is_shared: bool = False
    permissions: list[FilePermissionEntry] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create(
        cls,
        name: str,
        workspace_id: Id,
        owner_id: Id,
        folder_type: FolderType = FolderType.REGULAR,
        parent_folder_id: Id | None = None,
    ) -> Folder:
        """Создаёт папку."""
        folder = cls(
            name=name,
            workspace_id=workspace_id,
            owner_id=owner_id,
            folder_type=folder_type,
            parent_folder_id=parent_folder_id,
        )
        folder._register_event(
            FolderCreated(
                folder_id=str(folder.id),
                workspace_id=str(workspace_id),
                folder_type=folder_type,
            )
        )
        return folder

    @classmethod
    def create_project_folder(cls, name: str, workspace_id: Id, project_id: Id, owner_id: Id) -> Folder:
        """Создаёт папку проекта."""
        folder = cls(
            name=name,
            workspace_id=workspace_id,
            owner_id=owner_id,
            folder_type=FolderType.PROJECT,
            project_id=project_id,
        )
        folder._register_event(
            FolderCreated(
                folder_id=str(folder.id),
                workspace_id=str(workspace_id),
                folder_type=FolderType.PROJECT,
            )
        )
        return folder

    # --- Инварианты ---

    def _assert_can_modify(self) -> None:
        if self.folder_type == FolderType.SYSTEM:
            raise ValueError("Системную папку нельзя изменять")

    # --- Информация ---

    def rename(self, new_name: str) -> None:
        self._assert_can_modify()
        self.name = new_name
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            FolderUpdated(folder_id=str(self.id), changed_fields=["name"])
        )

    def move(self, new_parent_folder_id: Id) -> None:
        self._assert_can_modify()
        old_parent_id = self.parent_folder_id
        self.parent_folder_id = new_parent_folder_id
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            FolderMoved(
                folder_id=str(self.id),
                old_parent_id=str(old_parent_id) if old_parent_id else "",
                new_parent_id=str(new_parent_folder_id),
            )
        )

    def update_description(self, description: str | None) -> None:
        self._assert_can_modify()
        self.description = description
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            FolderUpdated(folder_id=str(self.id), changed_fields=["description"])
        )

    def pin(self) -> None:
        self.is_pinned = True
        self.updated_at = datetime.now(tz=timezone.utc)

    def unpin(self) -> None:
        self.is_pinned = False
        self.updated_at = datetime.now(tz=timezone.utc)

    def share(self) -> None:
        self.is_shared = True
        self.updated_at = datetime.now(tz=timezone.utc)

    def unshare(self) -> None:
        self.is_shared = False
        self.updated_at = datetime.now(tz=timezone.utc)

    # --- Разрешения ---

    def grant_permission(self, access_level: FileAccessLevel, granted_by: Id, user_id: Id | None = None, team_id: Id | None = None) -> None:
        if user_id is None and team_id is None:
            raise ValueError("Хотя бы один из user_id/team_id должен быть заполнен")
        entry = FilePermissionEntry(
            user_id=user_id,
            team_id=team_id,
            access_level=access_level,
            granted_by=granted_by,
        )
        self.permissions.append(entry)
        self.updated_at = datetime.now(tz=timezone.utc)

    def revoke_permission(self, user_id: Id | None = None, team_id: Id | None = None) -> None:
        self.permissions = [
            p for p in self.permissions
            if not (
                (user_id is not None and p.user_id == user_id)
                or (team_id is not None and p.team_id == team_id)
            )
        ]
        self.updated_at = datetime.now(tz=timezone.utc)

    # --- Удаление ---

    def delete(self) -> None:
        self._assert_can_modify()
        self._register_event(FolderDeleted(folder_id=str(self.id)))
