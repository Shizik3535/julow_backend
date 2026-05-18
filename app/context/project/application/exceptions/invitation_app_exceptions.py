from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class DuplicateInvitationForEmailException(ApplicationException):
    """Уже существует активное приглашение в проект для указанного email."""

    def __init__(self, email: str, project_id: str) -> None:
        super().__init__(
            f"В проект {project_id} уже отправлено приглашение для {email}"
        )
        self.email = email
        self.project_id = project_id


class InvitationAlreadyAcceptedException(ApplicationException):
    """Приглашение уже принято/обработано."""

    def __init__(self, invitation_id: str) -> None:
        super().__init__(f"Приглашение {invitation_id} уже обработано")
        self.invitation_id = invitation_id
