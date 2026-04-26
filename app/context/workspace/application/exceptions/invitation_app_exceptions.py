from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class InvitationAlreadyProcessedException(ApplicationException):
    """Приглашение уже обработано (принято/отклонено/отозвано)."""

    def __init__(self, invitation_id: str) -> None:
        super().__init__(f"Приглашение {invitation_id} уже обработано")
        self.invitation_id = invitation_id


class DuplicateInvitationForEmailException(ApplicationException):
    """Приглашение для этого email уже существует в workspace."""

    http_status_code = 409
    error_code = "DUPLICATE_INVITATION"

    def __init__(self, email: str, workspace_id: str) -> None:
        super().__init__(
            f"Приглашение для {email} уже существует в workspace {workspace_id}"
        )
        self.email = email
        self.workspace_id = workspace_id
