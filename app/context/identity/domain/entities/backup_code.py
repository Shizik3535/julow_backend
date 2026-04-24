from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity


@dataclass
class BackupCode(BaseEntity):
    """
    Сущность резервного кода для 2FA.

    Принадлежит агрегату User. Хранит хеш кода,
    а не сам код. Генерация и хеширование — инфраструктурный concern.

    Атрибуты:
        id: Уникальный идентификатор записи.
        code_hash: Хеш резервного кода.
        is_used: Был ли код использован.
        used_at: Время использования кода.
        created_at: Время создания кода.
    """

    code_hash: str = ""
    is_used: bool = False
    used_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    def mark_used(self) -> None:
        """Помечает код как использованный."""
        self.is_used = True
        self.used_at = datetime.now(tz=timezone.utc)
