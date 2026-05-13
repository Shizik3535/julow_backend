from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class AnalyticsWorkspaceNotFoundException(ApplicationException):
    """Workspace не найден при операции аналитики."""

    http_status_code = 404
    error_code = "WORKSPACE_NOT_FOUND"

    def __init__(self, workspace_id: str) -> None:
        super().__init__(f"Workspace {workspace_id} не найден")
        self.workspace_id = workspace_id


class AnalyticsProjectNotFoundException(ApplicationException):
    """Проект не найден при операции аналитики."""

    http_status_code = 404
    error_code = "PROJECT_NOT_FOUND"

    def __init__(self, project_id: str) -> None:
        super().__init__(f"Проект {project_id} не найден")
        self.project_id = project_id


class DashboardLimitExceededException(ApplicationException):
    """Превышен лимит дашбордов по тарифу."""

    http_status_code = 402
    error_code = "DASHBOARD_LIMIT_EXCEEDED"

    def __init__(self, limit: int) -> None:
        super().__init__(f"Превышен лимит дашбордов: {limit}")
        self.limit = limit


class WidgetLimitExceededException(ApplicationException):
    """Превышен лимит виджетов на дашборд."""

    http_status_code = 402
    error_code = "WIDGET_LIMIT_EXCEEDED"

    def __init__(self, limit: int) -> None:
        super().__init__(f"Превышен лимит виджетов на дашборд: {limit}")
        self.limit = limit


class ReportJobNotFoundException(ApplicationException):
    """Задание на генерацию отчёта не найдено."""

    http_status_code = 404
    error_code = "REPORT_JOB_NOT_FOUND"

    def __init__(self, job_id: str) -> None:
        super().__init__(f"Задание генерации отчёта {job_id} не найдено")
        self.job_id = job_id


class ReportGenerationUnavailableException(ApplicationException):
    """Генерация отчёта невозможна (нет провайдера/тариф запрещает)."""

    http_status_code = 503
    error_code = "REPORT_GENERATION_UNAVAILABLE"

    def __init__(self, reason: str = "") -> None:
        msg = "Генерация отчёта недоступна"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


class AnalyticsQueryExecutionException(ApplicationException):
    """Ошибка выполнения аналитического запроса на стороне источника BC."""

    http_status_code = 502
    error_code = "ANALYTICS_QUERY_EXECUTION_FAILED"

    def __init__(self, detail: str = "") -> None:
        msg = "Не удалось выполнить аналитический запрос"
        if detail:
            msg += f": {detail}"
        super().__init__(msg)


class InvalidAdHocReportRequestException(ApplicationException):
    """Некорректный ad-hoc запрос на генерацию отчёта (нет report_type/query)."""

    http_status_code = 400
    error_code = "INVALID_AD_HOC_REPORT_REQUEST"

    def __init__(self, detail: str = "") -> None:
        msg = "Ad-hoc-генерация требует report_type и query"
        if detail:
            msg += f": {detail}"
        super().__init__(msg)


class ReportScheduleRequiredException(ApplicationException):
    """Операция требует, чтобы у отчёта было задано активное расписание."""

    http_status_code = 400
    error_code = "REPORT_SCHEDULE_REQUIRED"

    def __init__(self, report_id: str) -> None:
        super().__init__(f"У отчёта {report_id} нет расписания")
        self.report_id = report_id


class InvalidShareAccessLevelException(ApplicationException):
    """Некорректный уровень доступа при шаринге."""

    http_status_code = 400
    error_code = "INVALID_SHARE_ACCESS_LEVEL"

    def __init__(self, value: str) -> None:
        super().__init__(f"Некорректный уровень доступа: {value}")
        self.value = value


class UnsupportedDataSourceException(ApplicationException):
    """Для DataSource нет резолвера (BC недоступен/не интегрирован)."""

    http_status_code = 501
    error_code = "UNSUPPORTED_DATA_SOURCE"

    def __init__(self, data_source: str) -> None:
        super().__init__(f"Для источника данных «{data_source}» нет резолвера")
        self.data_source = data_source
