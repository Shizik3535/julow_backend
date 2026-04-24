from __future__ import annotations

from app.shared.domain.exceptions import EntityNotFoundException


class ChangelogNotFoundException(EntityNotFoundException):
    """Запись истории изменений не найдена."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="ChangelogEntry", id=id)
