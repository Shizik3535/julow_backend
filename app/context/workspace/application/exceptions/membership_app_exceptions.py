from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class MemberAlreadyExistsException(ApplicationException):
    """Пользователь уже является участником workspace."""

    def __init__(self, user_id: str, workspace_id: str) -> None:
        super().__init__(
            f"Пользователь {user_id} уже является участником workspace {workspace_id}"
        )
        self.user_id = user_id
        self.workspace_id = workspace_id


class MemberNotInWorkspaceException(ApplicationException):
    """Пользователь не является участником workspace."""

    def __init__(self, user_id: str, workspace_id: str) -> None:
        super().__init__(
            f"Пользователь {user_id} не является участником workspace {workspace_id}"
        )
        self.user_id = user_id
        self.workspace_id = workspace_id


class UserNotFoundException(ApplicationException):
    """Пользователь не найден в Identity BC."""

    def __init__(self, user_id: str) -> None:
        super().__init__(f"Пользователь {user_id} не найден")
        self.user_id = user_id
