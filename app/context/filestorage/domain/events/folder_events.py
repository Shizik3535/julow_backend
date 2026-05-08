from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_domain_event import BaseDomainEvent
from app.context.filestorage.domain.value_objects.folder_type import FolderType


@dataclass(frozen=True)
class FolderCreated(BaseDomainEvent):
    """Папка создана."""

    folder_id: str = ""
    workspace_id: str = ""
    folder_type: FolderType = FolderType.REGULAR


@dataclass(frozen=True)
class FolderUpdated(BaseDomainEvent):
    """Папка обновлена."""

    folder_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FolderDeleted(BaseDomainEvent):
    """Папка удалена."""

    folder_id: str = ""


@dataclass(frozen=True)
class FolderMoved(BaseDomainEvent):
    """Папка перемещена."""

    folder_id: str = ""
    old_parent_id: str = ""
    new_parent_id: str = ""


@dataclass(frozen=True)
class FolderPinned(BaseDomainEvent):
    """Папка закреплена."""

    folder_id: str = ""


@dataclass(frozen=True)
class FolderUnpinned(BaseDomainEvent):
    """Папка откреплена."""

    folder_id: str = ""


@dataclass(frozen=True)
class FolderShared(BaseDomainEvent):
    """Папка расшарена."""

    folder_id: str = ""


@dataclass(frozen=True)
class FolderUnshared(BaseDomainEvent):
    """Шаринг папки отменён."""

    folder_id: str = ""
