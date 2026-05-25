from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class InsufficientChatPermissionsException(ApplicationException):
    """У пользователя нет необходимой роли в чате для операции."""

    http_status_code = 403
    error_code = "INSUFFICIENT_CHAT_PERMISSIONS"

    def __init__(self, chat_id: str, required_roles: list[str]) -> None:
        self.chat_id = chat_id
        self.required_roles = required_roles
        super().__init__(
            f"Недостаточно прав в чате {chat_id}: "
            f"требуется одна из ролей {required_roles}"
        )


class NotMessageAuthorException(ApplicationException):
    """Пользователь не является автором сообщения."""

    http_status_code = 403
    error_code = "NOT_MESSAGE_AUTHOR"

    def __init__(self) -> None:
        super().__init__("Только автор сообщения может выполнить эту операцию")


class NotMeetingOrganizerException(ApplicationException):
    """Только организатор совещания может выполнить эту операцию."""

    http_status_code = 403
    error_code = "NOT_MEETING_ORGANIZER"

    def __init__(self) -> None:
        super().__init__("Только организатор совещания может выполнить эту операцию")


class NotMeetingParticipantException(ApplicationException):
    """Только участник совещания может выполнить эту операцию."""

    http_status_code = 403
    error_code = "NOT_MEETING_PARTICIPANT"

    def __init__(self) -> None:
        super().__init__("Только участник совещания может выполнить эту операцию")


class ConferenceProviderNotImplementedException(ApplicationException):
    """Провайдер конференции пока не поддержан."""

    http_status_code = 501
    error_code = "CONFERENCE_PROVIDER_NOT_IMPLEMENTED"

    def __init__(self, provider: str) -> None:
        self.provider = provider
        super().__init__(
            f"Провайдер видеоконференции «{provider}» пока не поддержан"
        )


class CannotPostToAnnouncementException(ApplicationException):
    """Только OWNER/ADMIN канала объявлений могут постить сообщения."""

    http_status_code = 403
    error_code = "CANNOT_POST_TO_ANNOUNCEMENT"

    def __init__(self) -> None:
        super().__init__(
            "Только владелец или администратор канала объявлений могут публиковать сообщения"
        )


class CommentTargetForbiddenException(ApplicationException):
    """
    У пользователя нет доступа к комментируемой сущности.

    Communication BC не является источником истины для прав;
    проверка делегируется в parent BC (Project/Task/...) через
    CommentTargetAccessPort.
    """

    http_status_code = 403
    error_code = "COMMENT_TARGET_FORBIDDEN"

    def __init__(
        self,
        target_type: str,
        target_id: str,
        user_id: str | None = None,
        reason: str | None = None,
    ) -> None:
        self.target_type = target_type
        self.target_id = target_id
        self.user_id = user_id
        self.reason = reason
        suffix = f": {reason}" if reason else ""
        super().__init__(
            f"Нет доступа к комментариям сущности {target_type}={target_id}{suffix}"
        )


class InsufficientMeetingCreatePermissionsException(ApplicationException):
    """Только OWNER/ADMIN/MANAGER проекта могут создавать совещания."""

    http_status_code = 403
    error_code = "INSUFFICIENT_MEETING_CREATE_PERMISSIONS"

    def __init__(self, project_id: str) -> None:
        self.project_id = project_id
        super().__init__(
            "Недостаточно прав для создания совещания: требуется роль owner/admin/manager "
            f"в проекте {project_id}"
        )
