from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.context.analytics.domain.value_objects.report_type import ReportType
from app.context.analytics.domain.value_objects.analytics_query import AnalyticsQuery
from app.context.analytics.domain.value_objects.export_format import ExportFormat
from app.context.analytics.domain.value_objects.share_access_level import ShareAccessLevel
from app.context.analytics.domain.entities.report_schedule import ReportSchedule
from app.context.analytics.domain.entities.report_share import ReportShare
from app.context.analytics.domain.events.report_events import (
    ReportCreated,
    ReportUpdated,
    ReportGenerated,
    ReportScheduled,
    ReportScheduleDeactivated,
    ReportExported,
    ReportShared,
    ReportUnshared,
    ReportDeleted,
)
from app.context.analytics.domain.exceptions.dashboard_exceptions import (
    DuplicateShareException,
    CannotShareWithSelfException,
)
from app.context.analytics.domain.exceptions.report_exceptions import NoRecipientsException


@dataclass
class Report(AggregateRoot):
    """Корень агрегата отчёта (Analytics BC)."""

    owner_id: Id = field(default_factory=Id.generate)
    workspace_id: Id | None = None
    name: str = ""
    description: str | None = None
    report_type: ReportType = ReportType.CUSTOM
    query: AnalyticsQuery = field(default_factory=lambda: AnalyticsQuery(raw=True))
    schedule: ReportSchedule | None = None
    shares: list[ReportShare] = field(default_factory=list)
    last_generated_at: datetime | None = None
    last_export_format: ExportFormat | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create(
        cls,
        name: str,
        report_type: ReportType,
        query: AnalyticsQuery,
        owner_id: Id,
        workspace_id: Id | None = None,
        description: str | None = None,
    ) -> Report:
        report = cls(
            name=name,
            description=description,
            report_type=report_type,
            query=query,
            owner_id=owner_id,
            workspace_id=workspace_id,
        )
        report._register_event(ReportCreated(report_id=str(report.id), report_type=report_type))
        return report

    def update_info(self, name: str | None = None, description: str | None = None) -> None:
        changed: list[str] = []
        if name is not None and self.name != name:
            self.name = name
            changed.append("name")
        if description is not None and self.description != description:
            self.description = description
            changed.append("description")
        if changed:
            self.updated_at = datetime.now(tz=timezone.utc)
            self._register_event(ReportUpdated(report_id=str(self.id), changed_fields=changed))

    def update_query(self, query: AnalyticsQuery) -> None:
        if query == self.query:
            return
        self.query = query
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(ReportUpdated(report_id=str(self.id), changed_fields=["query"]))

    def set_schedule(self, schedule: ReportSchedule) -> None:
        if not schedule.recipients:
            raise NoRecipientsException()
        self.schedule = schedule
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(ReportScheduled(report_id=str(self.id), frequency=schedule.frequency))

    def remove_schedule(self) -> None:
        self.schedule = None
        self.updated_at = datetime.now(tz=timezone.utc)

    def deactivate_schedule(self) -> None:
        if self.schedule is not None:
            self.schedule.is_active = False
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(ReportScheduleDeactivated(report_id=str(self.id)))

    def mark_generated(self, generated_by: Id) -> None:
        self.last_generated_at = datetime.now(tz=timezone.utc)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(ReportGenerated(report_id=str(self.id), generated_by=str(generated_by)))

    def mark_exported(self, fmt: ExportFormat) -> None:
        self.last_export_format = fmt
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(ReportExported(report_id=str(self.id), format=fmt))

    def share(self, user_id: Id, access_level: ShareAccessLevel) -> None:
        if user_id == self.owner_id:
            raise CannotShareWithSelfException()
        if any(s.user_id == user_id for s in self.shares):
            raise DuplicateShareException()
        share = ReportShare(user_id=user_id, access_level=access_level)
        self.shares.append(share)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(ReportShared(report_id=str(self.id), user_id=str(user_id), access_level=access_level))

    def unshare(self, user_id: Id) -> None:
        self.shares = [s for s in self.shares if s.user_id != user_id]
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(ReportUnshared(report_id=str(self.id), user_id=str(user_id)))

    def delete(self) -> None:
        self._register_event(ReportDeleted(report_id=str(self.id)))
