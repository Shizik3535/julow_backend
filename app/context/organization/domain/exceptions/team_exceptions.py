from __future__ import annotations

from app.shared.domain.exceptions import EntityNotFoundException, BusinessRuleViolationException


class TeamNotFoundException(EntityNotFoundException):
    """Команда не найдена."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="Team", id=id)


class TeamMemberAlreadyExistsException(BusinessRuleViolationException):
    """Участник уже состоит в команде."""

    def __init__(self, user_id: str = "", team_id: str = "") -> None:
        super().__init__(
            rule="TeamMemberAlreadyExists",
            message=f"Участник {user_id} уже состоит в команде {team_id}",
        )


class TeamAlreadyDeactivatedException(BusinessRuleViolationException):
    """Команда уже деактивирована."""

    def __init__(self, team_id: str = "") -> None:
        super().__init__(
            rule="TeamAlreadyDeactivated",
            message=f"Команда {team_id} уже деактивирована",
        )


class TeamDeactivatedException(BusinessRuleViolationException):
    """Команда деактивирована, операция невозможна."""

    def __init__(self, team_id: str = "") -> None:
        super().__init__(
            rule="TeamDeactivated",
            message=f"Команда {team_id} деактивирована" if team_id else "Команда деактивирована",
        )


class TeamAlreadyActiveException(BusinessRuleViolationException):
    """Команда уже активна."""

    def __init__(self, team_id: str = "") -> None:
        super().__init__(
            rule="TeamAlreadyActive",
            message=f"Команда {team_id} уже активна",
        )
