from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.color_vo import Color
from app.context.filestorage.domain.value_objects.file_type import FileType
from app.context.filestorage.domain.value_objects.file_size import FileSize
from app.context.filestorage.domain.value_objects.file_status import FileStatus
from app.context.filestorage.domain.value_objects.file_access_level import FileAccessLevel
from app.context.filestorage.domain.value_objects.virus_scan_status import VirusScanStatus
from app.context.filestorage.domain.entities.file_version import FileVersion
from app.context.filestorage.domain.entities.file_permission_entry import FilePermissionEntry
from app.context.filestorage.domain.entities.public_share_link import PublicShareLink
from app.context.filestorage.domain.entities.file_lock import FileLock
from app.context.filestorage.domain.entities.file_tag import FileTag
from app.context.filestorage.domain.events.file_events import (
    FileUploaded,
    FileTrashed,
    FileRestored,
    FileDeleted,
    FileMoved,
    FileRenamed,
    FilePermissionGranted,
    FilePermissionRevoked,
    FileVersionCreated,
    FileLocked,
    FileUnlocked,
    PublicShareLinkCreated,
    PublicShareLinkRevoked,
    PublicShareLinkAccessed,
    FileTagAdded,
    FileTagRemoved,
    VirusDetected,
    VirusScanCompleted,
)
from app.context.filestorage.domain.exceptions.file_exceptions import (
    FileTrashedException,
    FileLockedException,
    VirusDetectedException,
    PublicShareLinkExpiredException,
    PublicShareLinkMaxUsesExceededException,
    InvalidSharePasswordException,
    DuplicateFileTagException,
    CannotLockFileException,
    CannotUnlockFileException,
)


@dataclass
class File(AggregateRoot):
    """
    Корень агрегата файла (FileStorage BC).

    Атрибуты:
        name: Имя файла.
        original_name: Оригинальное имя при загрузке.
        file_type: Тип файла.
        size: Размер файла.
        mime_type: MIME-тип.
        storage_id: Opaque ID хранилища.
        storage_path: Путь в хранилище.
        folder_id: Opaque ID папки.
        uploader_id: ID загрузившего.
        workspace_id: Opaque ID workspace.
        owner_id: ID владельца.
        description: Описание.
        scan_status: Статус сканирования на вирусы.
        status: Жизненный цикл файла.
        permissions: Список разрешений.
        versions: Список версий.
        lock: Блокировка (None — не заблокирован).
        tags: Список тегов.
        share_links: Список публичных ссылок.
        preview_path: Путь к превью.
        is_shared: Расшарен ли файл.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    name: str = ""
    original_name: str = ""
    file_type: FileType = FileType.OTHER
    size: FileSize = field(default_factory=lambda: FileSize(value=0))
    mime_type: str = ""
    storage_id: Id = field(default_factory=Id.generate)
    storage_path: str = ""
    folder_id: Id | None = None
    uploader_id: Id = field(default_factory=Id.generate)
    workspace_id: Id = field(default_factory=Id.generate)
    owner_id: Id = field(default_factory=Id.generate)
    description: str | None = None
    scan_status: VirusScanStatus = VirusScanStatus.PENDING
    status: FileStatus = FileStatus.ACTIVE
    permissions: list[FilePermissionEntry] = field(default_factory=list)
    versions: list[FileVersion] = field(default_factory=list)
    lock: FileLock | None = None
    tags: list[FileTag] = field(default_factory=list)
    share_links: list[PublicShareLink] = field(default_factory=list)
    preview_path: str | None = None
    is_shared: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create(
        cls,
        name: str,
        original_name: str,
        file_type: FileType,
        size: FileSize,
        mime_type: str,
        storage_id: Id,
        storage_path: str,
        uploader_id: Id,
        workspace_id: Id,
        folder_id: Id | None = None,
    ) -> File:
        """Создаёт файл. owner_id = uploader_id."""
        file = cls(
            name=name,
            original_name=original_name,
            file_type=file_type,
            size=size,
            mime_type=mime_type,
            storage_id=storage_id,
            storage_path=storage_path,
            uploader_id=uploader_id,
            workspace_id=workspace_id,
            owner_id=uploader_id,
            folder_id=folder_id,
        )
        file._register_event(
            FileUploaded(
                file_id=str(file.id),
                uploader_id=str(uploader_id),
                workspace_id=str(workspace_id),
                file_type=file_type,
                size_bytes=size.value,
            )
        )
        return file

    # --- Инварианты ---

    def _assert_can_modify(self) -> None:
        if self.status == FileStatus.TRASHED:
            raise FileTrashedException()
        if self.status == FileStatus.DELETED:
            raise FileTrashedException()
        if self.lock is not None:
            raise FileLockedException()
        if self.scan_status == VirusScanStatus.INFECTED:
            raise VirusDetectedException()

    # --- Информация ---

    def rename(self, new_name: str) -> None:
        self._assert_can_modify()
        old_name = self.name
        self.name = new_name
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            FileRenamed(file_id=str(self.id), old_name=old_name, new_name=new_name)
        )

    def move(self, new_folder_id: Id) -> None:
        self._assert_can_modify()
        old_folder_id = self.folder_id
        self.folder_id = new_folder_id
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            FileMoved(
                file_id=str(self.id),
                old_folder_id=str(old_folder_id) if old_folder_id else "",
                new_folder_id=str(new_folder_id),
            )
        )

    def update_description(self, description: str | None) -> None:
        self._assert_can_modify()
        self.description = description
        self.updated_at = datetime.now(tz=timezone.utc)

    # --- Жизненный цикл ---

    def trash(self, trashed_by: Id) -> None:
        if self.status != FileStatus.ACTIVE:
            return
        self.status = FileStatus.TRASHED
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            FileTrashed(file_id=str(self.id), trashed_by=str(trashed_by))
        )

    def restore(self, restored_by: Id) -> None:
        if self.status != FileStatus.TRASHED:
            return
        self.status = FileStatus.ACTIVE
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            FileRestored(file_id=str(self.id), restored_by=str(restored_by))
        )

    def delete_permanently(self) -> None:
        if self.status == FileStatus.DELETED:
            return
        self.status = FileStatus.DELETED
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(FileDeleted(file_id=str(self.id)))

    # --- Virus scan ---

    def mark_scan_clean(self) -> None:
        self.scan_status = VirusScanStatus.CLEAN
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            VirusScanCompleted(file_id=str(self.id), scan_status=VirusScanStatus.CLEAN)
        )

    def mark_scan_infected(self, virus_name: str | None = None) -> None:
        self.scan_status = VirusScanStatus.INFECTED
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            VirusDetected(file_id=str(self.id), virus_name=virus_name or "")
        )

    def mark_scan_error(self) -> None:
        self.scan_status = VirusScanStatus.ERROR
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            VirusScanCompleted(file_id=str(self.id), scan_status=VirusScanStatus.ERROR)
        )

    # --- Версии ---

    def add_version(self, storage_path: str, size_bytes: int, uploader_id: Id, change_summary: str | None = None) -> FileVersion:
        self._assert_can_modify()
        version_number = len(self.versions) + 1
        version = FileVersion(
            version_number=version_number,
            storage_path=storage_path,
            size_bytes=size_bytes,
            uploader_id=uploader_id,
            change_summary=change_summary,
        )
        self.versions.append(version)
        self.storage_path = storage_path
        self.size = FileSize(value=size_bytes)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            FileVersionCreated(
                file_id=str(self.id), version_number=version_number, uploader_id=str(uploader_id)
            )
        )
        return version

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
        self._register_event(
            FilePermissionGranted(
                file_id=str(self.id),
                user_id=str(user_id) if user_id else "",
                team_id=str(team_id) if team_id else "",
                access_level=access_level,
            )
        )

    def revoke_permission(self, user_id: Id | None = None, team_id: Id | None = None) -> None:
        self.permissions = [
            p for p in self.permissions
            if not (
                (user_id is not None and p.user_id == user_id)
                or (team_id is not None and p.team_id == team_id)
            )
        ]
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            FilePermissionRevoked(
                file_id=str(self.id),
                user_id=str(user_id) if user_id else "",
                team_id=str(team_id) if team_id else "",
            )
        )

    # --- Блокировки ---

    def lock_file(self, locked_by: Id, reason: str | None = None, expires_at: datetime | None = None) -> None:
        if self.lock is not None:
            raise CannotLockFileException(reason="уже заблокирован")
        if self.status != FileStatus.ACTIVE:
            raise CannotLockFileException(reason="файл не активен")
        self.lock = FileLock(locked_by=locked_by, reason=reason, expires_at=expires_at)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            FileLocked(file_id=str(self.id), locked_by=str(locked_by))
        )

    def unlock(self, unlocked_by: Id) -> None:
        if self.lock is None:
            return
        if self.lock.locked_by != unlocked_by:
            raise CannotUnlockFileException()
        self.lock = None
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            FileUnlocked(file_id=str(self.id), unlocked_by=str(unlocked_by))
        )

    # --- Теги ---

    def add_tag(self, tag: FileTag) -> None:
        if any(t.name == tag.name for t in self.tags):
            raise DuplicateFileTagException(name=tag.name)
        self.tags.append(tag)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            FileTagAdded(file_id=str(self.id), tag_name=tag.name)
        )

    def remove_tag(self, tag_name: str) -> None:
        self.tags = [t for t in self.tags if t.name != tag_name]
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            FileTagRemoved(file_id=str(self.id), tag_name=tag_name)
        )

    # --- Публичные ссылки ---

    def create_share_link(
        self,
        token: str,
        access_level: FileAccessLevel,
        created_by: Id,
        password_hash: str | None = None,
        expires_at: datetime | None = None,
        max_uses: int | None = None,
    ) -> PublicShareLink:
        link = PublicShareLink(
            token=token,
            password_hash=password_hash,
            expires_at=expires_at,
            access_level=access_level,
            max_uses=max_uses,
            created_by=created_by,
        )
        self.share_links.append(link)
        self.is_shared = True
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            PublicShareLinkCreated(file_id=str(self.id), link_id=str(link.id))
        )
        return link

    def revoke_share_link(self, link_id: Id) -> None:
        self.share_links = [l for l in self.share_links if l.id != link_id]
        if not self.share_links:
            self.is_shared = False
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            PublicShareLinkRevoked(file_id=str(self.id), link_id=str(link_id))
        )

    def access_share_link(self, token: str, password: str | None = None) -> None:
        link = next((l for l in self.share_links if l.token == token), None)
        if link is None:
            return
        if link.expires_at is not None and datetime.now(tz=timezone.utc) > link.expires_at:
            raise PublicShareLinkExpiredException()
        if link.max_uses is not None and link.current_uses >= link.max_uses:
            raise PublicShareLinkMaxUsesExceededException()
        if link.password_hash is not None and password is None:
            raise InvalidSharePasswordException()
        link.current_uses += 1
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            PublicShareLinkAccessed(file_id=str(self.id), link_id=str(link.id))
        )

    # --- Превью ---

    def set_preview(self, preview_path: str) -> None:
        self.preview_path = preview_path
        self.updated_at = datetime.now(tz=timezone.utc)
