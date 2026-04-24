from __future__ import annotations

from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class ReportNotFoundException(EntityNotFoundException):
    def __init__(self, id: object) -> None:
        super().__init__(entity_type="Report", id=id)


class ReportScheduleNotFoundException(EntityNotFoundException):
    def __init__(self, id: object) -> None:
        super().__init__(entity_type="ReportSchedule", id=id)


class ReportShareNotFoundException(EntityNotFoundException):
    def __init__(self, id: object) -> None:
        super().__init__(entity_type="ReportShare", id=id)


class InvalidDataSourceException(BusinessRuleViolationException):
    def __init__(self, data_source: str = "") -> None:
        super().__init__(rule="ValidDataSource", message=f"Некорректный источник данных{f': {data_source}' if data_source else ''}")


class InvalidFilterOperatorException(BusinessRuleViolationException):
    def __init__(self, operator: str = "") -> None:
        super().__init__(rule="ValidFilterOperator", message=f"Некорректный оператор фильтра{f': {operator}' if operator else ''}")


class InvalidWidgetSizeException(BusinessRuleViolationException):
    def __init__(self, detail: str = "") -> None:
        super().__init__(rule="ValidWidgetSize", message=f"Некорректный размер виджета{f': {detail}' if detail else ''}")


class ReportExportFormatException(BusinessRuleViolationException):
    def __init__(self, fmt: str = "") -> None:
        super().__init__(rule="ValidExportFormat", message=f"Некорректный формат экспорта{f': {fmt}' if fmt else ''}")


class InvalidReportFrequencyException(BusinessRuleViolationException):
    def __init__(self, freq: str = "") -> None:
        super().__init__(rule="ValidReportFrequency", message=f"Некорректная частота расписания{f': {freq}' if freq else ''}")
