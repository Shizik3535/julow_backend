from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class MemberAlreadyExistsException(ApplicationException):
    """Пользователь уже является участником организации."""

    def __init__(self, user_id: str, org_id: str) -> None:
        super().__init__(
            f"Пользователь {user_id} уже является участником организации {org_id}"
        )
        self.user_id = user_id
        self.org_id = org_id


class MemberNotInOrganizationException(ApplicationException):
    """Пользователь не является участником организации."""

    def __init__(self, user_id: str, org_id: str) -> None:
        super().__init__(
            f"Пользователь {user_id} не является участником организации {org_id}"
        )
        self.user_id = user_id
        self.org_id = org_id


class UserNotFoundException(ApplicationException):
    """Пользователь не найден в Identity BC."""

    def __init__(self, user_id: str) -> None:
        super().__init__(f"Пользователь {user_id} не найден")
        self.user_id = user_id
