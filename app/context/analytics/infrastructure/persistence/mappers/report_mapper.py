from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.analytics.domain.aggregates.report import Report
from app.context.analytics.domain.entities.report_schedule import ReportSchedule
from app.context.analytics.domain.entities.report_share import ReportShare
from app.context.analytics.domain.value_objects.export_format import ExportFormat
from app.context.analytics.domain.value_objects.report_frequency import ReportFrequency
from app.context.analytics.domain.value_objects.report_type import ReportType
from app.context.analytics.domain.value_objects.share_access_level import ShareAccessLevel
from app.context.analytics.infrastructure.persistence.mappers._query_serialization import (
    analytics_query_from_json,
    analytics_query_to_json,
)
from app.context.analytics.infrastructure.persistence.orm_models.report_orm import (
    ReportORM,
    ReportShareORM,
)


class ReportMapper(BaseMapper[Report, ReportORM]):
    """Data Mapper: ``Report`` ↔ ``ReportORM``.

    ``query.data_source`` и ``query.bounded_context`` денормализуются в
    отдельные индексируемые колонки — это требование
    ``ReportRepository`` (фильтрация по data_source / bounded_context).
    """

    def to_domain(self, orm_model: ReportORM) -> Report:
        query = analytics_query_from_json(orm_model.query)
        schedule = self._schedule_to_domain(orm_model)
        shares = [self._share_to_domain(s) for s in (orm_model.shares or [])]
        return Report(
            id=self._map_id(orm_model.id),
            owner_id=self._map_id(orm_model.owner_id),
            workspace_id=(
                self._map_id(orm_model.workspace_id)
                if orm_model.workspace_id
                else None
            ),
            name=orm_model.name,
            description=orm_model.description,
            report_type=ReportType(orm_model.report_type),
            query=query,
            schedule=schedule,
            shares=shares,
            last_generated_at=orm_model.last_generated_at,
            last_export_format=(
                ExportFormat(orm_model.last_export_format)
                if orm_model.last_export_format
                else None
            ),
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: Report) -> ReportORM:
        orm = ReportORM(
            id=self._map_uuid(aggregate.id),
            owner_id=self._map_uuid(aggregate.owner_id),
            workspace_id=(
                self._map_uuid(aggregate.workspace_id)
                if aggregate.workspace_id
                else None
            ),
            name=aggregate.name,
            description=aggregate.description,
            report_type=aggregate.report_type.value,
            query=analytics_query_to_json(aggregate.query),
            query_data_source=aggregate.query.data_source.value,
            query_bounded_context=aggregate.query.bounded_context.value,
            schedule_frequency=(
                aggregate.schedule.frequency.value if aggregate.schedule else None
            ),
            schedule_recipients=(
                [str(r) for r in aggregate.schedule.recipients]
                if aggregate.schedule
                else None
            ),
            schedule_is_active=(
                aggregate.schedule.is_active if aggregate.schedule else False
            ),
            schedule_next_run_at=(
                aggregate.schedule.next_run_at if aggregate.schedule else None
            ),
            schedule_last_run_at=(
                aggregate.schedule.last_run_at if aggregate.schedule else None
            ),
            last_generated_at=aggregate.last_generated_at,
            last_export_format=(
                aggregate.last_export_format.value
                if aggregate.last_export_format
                else None
            ),
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
        orm.shares = [
            self._share_to_orm(s, report_id=aggregate.id) for s in aggregate.shares
        ]
        return orm

    # ---- Schedule (встроенная сущность) ----

    def _schedule_to_domain(self, orm: ReportORM) -> ReportSchedule | None:
        if orm.schedule_frequency is None:
            return None
        recipients_raw = orm.schedule_recipients or []
        recipients = [self._map_id(uid) for uid in recipients_raw]
        return ReportSchedule(
            frequency=ReportFrequency(orm.schedule_frequency),
            recipients=recipients,
            is_active=orm.schedule_is_active,
            next_run_at=orm.schedule_next_run_at,
            last_run_at=orm.schedule_last_run_at,
        )

    # ---- Share ----

    def _share_to_domain(self, orm: ReportShareORM) -> ReportShare:
        return ReportShare(
            id=self._map_id(orm.id),
            user_id=self._map_id(orm.user_id),
            access_level=ShareAccessLevel(orm.access_level),
            shared_at=orm.shared_at,
        )

    def _share_to_orm(self, share: ReportShare, report_id: Id) -> ReportShareORM:
        return ReportShareORM(
            id=self._map_uuid(share.id),
            report_id=self._map_uuid(report_id),
            user_id=self._map_uuid(share.user_id),
            access_level=share.access_level.value,
            shared_at=share.shared_at,
        )
