from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class ProfileAlreadyExistsException(ApplicationException):
    """Профиль для данного пользователя уже существует."""

    def __init__(self, user_id: str) -> None:
        super().__init__(f"Профиль для пользователя {user_id} уже существует")
        self.user_id = user_id


class InvalidStartPageAppException(ApplicationException):
    """Стартовая страница не зарегистрирована в системе."""

    def __init__(self, page: str) -> None:
        super().__init__(f"Стартовая страница «{page}» не зарегистрирована")
        self.page = page


class OrganizationMembershipRequiredException(ApplicationException):
    """Пользователь не состоит в организации для ORGANIZATION_ONLY видимости."""

    def __init__(self, user_id: str, organization_id: str) -> None:
        super().__init__(
            f"Пользователь {user_id} не состоит в организации {organization_id}"
        )
        self.user_id = user_id
        self.organization_id = organization_id
