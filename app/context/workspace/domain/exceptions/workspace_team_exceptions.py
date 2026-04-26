from __future__ import annotations

from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class WorkspaceTeamNotFoundException(EntityNotFoundException):
    """Команда workspace не найдена."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="WorkspaceTeam", id=id)


class TeamMemberAlreadyExistsException(BusinessRuleViolationException):
    """Участник уже состоит в команде."""

    def __init__(self, user_id: object) -> None:
        super().__init__(
            rule="UniqueTeamMember",
            message=f"Участник {user_id} уже состоит в команде",
        )
