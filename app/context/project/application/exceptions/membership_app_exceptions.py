from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class UserNotFoundException(ApplicationException):
    """Пользователь не найден (через Identity BC)."""

    def __init__(self, user_id: str) -> None:
        super().__init__(f"Пользователь не найден: {user_id}")
        self.user_id = user_id


class MemberAlreadyExistsException(ApplicationException):
    """Участник уже состоит в проекте."""

    def __init__(self, user_id: str, project_id: str) -> None:
        super().__init__(f"Пользователь {user_id} уже участник проекта {project_id}")
        self.user_id = user_id
        self.project_id = project_id


class MemberNotInProjectException(ApplicationException):
    """Пользователь не является участником проекта."""

    def __init__(self, user_id: str, project_id: str) -> None:
        super().__init__(f"Пользователь {user_id} не является участником проекта {project_id}")
        self.user_id = user_id
        self.project_id = project_id


class MemberNotInWorkspaceException(ApplicationException):
    """Пользователь не является участником workspace (ACL)."""

    def __init__(self, user_id: str, workspace_id: str) -> None:
        super().__init__(f"Пользователь {user_id} не является участником workspace {workspace_id}")
        self.user_id = user_id
        self.workspace_id = workspace_id
