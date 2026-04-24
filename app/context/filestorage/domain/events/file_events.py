from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_domain_event import BaseDomainEvent
from app.context.filestorage.domain.value_objects.file_type import FileType
from app.context.filestorage.domain.value_objects.file_access_level import FileAccessLevel
from app.context.filestorage.domain.value_objects.virus_scan_status import VirusScanStatus


@dataclass(frozen=True)
class FileUploaded(BaseDomainEvent):
    """Файл загружен."""

    file_id: str = ""
    uploader_id: str = ""
    workspace_id: str = ""
    file_type: FileType = FileType.OTHER
    size_bytes: int = 0


@dataclass(frozen=True)
class FileDownloaded(BaseDomainEvent):
    """Файл скачан."""

    file_id: str = ""
    downloader_id: str = ""


@dataclass(frozen=True)
class FileTrashed(BaseDomainEvent):
    """Файл перемещён в корзину."""

    file_id: str = ""
    trashed_by: str = ""


@dataclass(frozen=True)
class FileRestored(BaseDomainEvent):
    """Файл восстановлен из корзины."""

    file_id: str = ""
    restored_by: str = ""


@dataclass(frozen=True)
class FileDeleted(BaseDomainEvent):
    """Файл окончательно удалён."""

    file_id: str = ""


@dataclass(frozen=True)
class FileMoved(BaseDomainEvent):
    """Файл перемещён."""

    file_id: str = ""
    old_folder_id: str = ""
    new_folder_id: str = ""


@dataclass(frozen=True)
class FileRenamed(BaseDomainEvent):
    """Файл переименован."""

    file_id: str = ""
    old_name: str = ""
    new_name: str = ""


@dataclass(frozen=True)
class FilePermissionGranted(BaseDomainEvent):
    """Разрешение на файл выдано."""

    file_id: str = ""
    user_id: str = ""
    team_id: str = ""
    access_level: FileAccessLevel = FileAccessLevel.VIEW


@dataclass(frozen=True)
class FilePermissionRevoked(BaseDomainEvent):
    """Разрешение на файл отозвано."""

    file_id: str = ""
    user_id: str = ""
    team_id: str = ""


@dataclass(frozen=True)
class FileVersionCreated(BaseDomainEvent):
    """Новая версия файла."""

    file_id: str = ""
    version_number: int = 1
    uploader_id: str = ""


@dataclass(frozen=True)
class FileLocked(BaseDomainEvent):
    """Файл заблокирован."""

    file_id: str = ""
    locked_by: str = ""


@dataclass(frozen=True)
class FileUnlocked(BaseDomainEvent):
    """Файл разблокирован."""

    file_id: str = ""
    unlocked_by: str = ""


@dataclass(frozen=True)
class PublicShareLinkCreated(BaseDomainEvent):
    """Публичная ссылка создана."""

    file_id: str = ""
    link_id: str = ""


@dataclass(frozen=True)
class PublicShareLinkRevoked(BaseDomainEvent):
    """Публичная ссылка отозвана."""

    file_id: str = ""
    link_id: str = ""


@dataclass(frozen=True)
class PublicShareLinkAccessed(BaseDomainEvent):
    """Переход по публичной ссылке."""

    file_id: str = ""
    link_id: str = ""


@dataclass(frozen=True)
class FileTagAdded(BaseDomainEvent):
    """Тег добавлен."""

    file_id: str = ""
    tag_name: str = ""


@dataclass(frozen=True)
class FileTagRemoved(BaseDomainEvent):
    """Тег удалён."""

    file_id: str = ""
    tag_name: str = ""


@dataclass(frozen=True)
class VirusDetected(BaseDomainEvent):
    """Вирус обнаружен."""

    file_id: str = ""
    virus_name: str = ""


@dataclass(frozen=True)
class VirusScanCompleted(BaseDomainEvent):
    """Сканирование завершено."""

    file_id: str = ""
    scan_status: VirusScanStatus = VirusScanStatus.CLEAN
