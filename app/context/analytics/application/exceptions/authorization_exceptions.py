from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class InsufficientAnalyticsPermissionsException(ApplicationException):
    """У пользователя нет необходимого разрешения в Analytics BC."""

    http_status_code = 403
    error_code = "INSUFFICIENT_ANALYTICS_PERMISSIONS"

    def __init__(self, permission: str, workspace_id: str, user_id: str | None = None) -> None:
        self.permission = permission
        self.workspace_id = workspace_id
        self.user_id = user_id
        super().__init__(
            f"Недостаточно прав в workspace {workspace_id}: "
            f"требуется разрешение «{permission}»"
        )


class AnalyticsAccessDeniedException(ApplicationException):
    """Доступ к ресурсу (дашборду/отчёту/шаблону) запрещён."""

    http_status_code = 403
    error_code = "ANALYTICS_ACCESS_DENIED"

    def __init__(self, resource: str, resource_id: str) -> None:
        super().__init__(f"Доступ к {resource} {resource_id} запрещён")
        self.resource = resource
        self.resource_id = resource_id
