from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id
from app.context.filestorage.domain.value_objects.file_access_level import FileAccessLevel


@dataclass
class FilePermissionEntry(BaseEntity):
    """
    Сущность разрешения на файл/папку.

    Хотя бы один из user_id/team_id заполнен.

    Атрибуты:
        user_id: ID пользователя (None — для команды).
        team_id: Opaque ID команды (None — для пользователя).
        access_level: Уровень доступа.
        granted_by: ID выдавшего разрешение.
        granted_at: Время выдачи.
    """

    user_id: Id | None = None
    team_id: Id | None = None
    access_level: FileAccessLevel = FileAccessLevel.VIEW
    granted_by: Id = field(default_factory=Id.generate)
    granted_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
