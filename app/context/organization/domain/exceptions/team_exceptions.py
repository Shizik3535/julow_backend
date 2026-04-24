from __future__ import annotations

from app.shared.domain.exceptions import EntityNotFoundException


class TeamNotFoundException(EntityNotFoundException):
    """Команда не найдена."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="Team", id=id)
