from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class WorkspaceLimits(ValueObject):
    """
    Лимиты workspace.

    Атрибуты:
        max_projects: Максимальное количество проектов (None — без ограничения).
        max_members: Максимальное количество участников (None — без ограничения).
        max_storage_bytes: Максимальный объём хранилища (None — без ограничения).
        max_file_size_bytes: Максимальный размер одного файла (None — без ограничения).
        max_teams: Максимальное количество команд (None — без ограничения).
    """

    max_projects: int | None = None
    max_members: int | None = None
    max_storage_bytes: int | None = None
    max_file_size_bytes: int | None = None
    max_teams: int | None = None

    def __post_init__(self) -> None:
        if self.max_projects is not None and self.max_projects < 0:
            raise ValidationException(
                field="max_projects",
                message="Максимальное количество проектов не может быть отрицательным",
            )
        if self.max_members is not None and self.max_members < 0:
            raise ValidationException(
                field="max_members",
                message="Максимальное количество участников не может быть отрицательным",
            )
        if self.max_storage_bytes is not None and self.max_storage_bytes < 0:
            raise ValidationException(
                field="max_storage_bytes",
                message="Максимальный объём хранилища не может быть отрицательным",
            )
        if self.max_file_size_bytes is not None and self.max_file_size_bytes < 0:
            raise ValidationException(
                field="max_file_size_bytes",
                message="Максимальный размер файла не может быть отрицательным",
            )
        if self.max_teams is not None and self.max_teams < 0:
            raise ValidationException(
                field="max_teams",
                message="Максимальное количество команд не может быть отрицательным",
            )
