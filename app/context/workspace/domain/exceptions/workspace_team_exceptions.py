from __future__ import annotations

from app.shared.domain.exceptions import EntityNotFoundException


class WorkspaceTeamNotFoundException(EntityNotFoundException):
    """Команда workspace не найдена."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="WorkspaceTeam", id=id)
