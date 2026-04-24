from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_domain_event import BaseDomainEvent
from app.context.analytics.domain.value_objects.report_type import ReportType
from app.context.analytics.domain.value_objects.export_format import ExportFormat
from app.context.analytics.domain.value_objects.report_frequency import ReportFrequency
from app.context.analytics.domain.value_objects.share_access_level import ShareAccessLevel


@dataclass(frozen=True)
class ReportCreated(BaseDomainEvent):
    report_id: str = ""
    report_type: ReportType = ReportType.CUSTOM


@dataclass(frozen=True)
class ReportUpdated(BaseDomainEvent):
    report_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ReportGenerated(BaseDomainEvent):
    report_id: str = ""
    generated_by: str = ""


@dataclass(frozen=True)
class ReportScheduled(BaseDomainEvent):
    report_id: str = ""
    frequency: ReportFrequency = ReportFrequency.WEEKLY


@dataclass(frozen=True)
class ReportScheduleDeactivated(BaseDomainEvent):
    report_id: str = ""


@dataclass(frozen=True)
class ReportExported(BaseDomainEvent):
    report_id: str = ""
    format: ExportFormat = ExportFormat.PDF


@dataclass(frozen=True)
class ReportShared(BaseDomainEvent):
    report_id: str = ""
    user_id: str = ""
    access_level: ShareAccessLevel = ShareAccessLevel.VIEW


@dataclass(frozen=True)
class ReportUnshared(BaseDomainEvent):
    report_id: str = ""
    user_id: str = ""


@dataclass(frozen=True)
class ReportDeleted(BaseDomainEvent):
    report_id: str = ""
