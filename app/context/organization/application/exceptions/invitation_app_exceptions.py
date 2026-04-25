from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class InvitationAlreadyProcessedException(ApplicationException):
    """Приглашение уже обработано (принято, отклонено или отозвано)."""

    def __init__(self, invitation_id: str) -> None:
        super().__init__(f"Приглашение {invitation_id} уже обработано")
        self.invitation_id = invitation_id


class DuplicateInvitationForEmailException(ApplicationException):
    """Активное приглашение для этого email уже существует."""

    http_status_code = 409
    error_code = "DUPLICATE_INVITATION"

    def __init__(self, email: str, org_id: str) -> None:
        super().__init__(
            f"Активное приглашение для {email} в организации {org_id} уже существует"
        )
        self.email = email
        self.org_id = org_id
