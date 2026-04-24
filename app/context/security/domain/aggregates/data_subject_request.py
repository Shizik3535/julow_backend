from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.context.security.domain.value_objects.data_subject_request_type import DataSubjectRequestType
from app.context.security.domain.value_objects.data_subject_request_status import DataSubjectRequestStatus
from app.context.security.domain.events.compliance_events import (
    DataSubjectRequestCreated,
    DataSubjectRequestCompleted,
    DataSubjectRequestRejected,
)
from app.context.security.domain.exceptions.backup_exceptions import DataSubjectRequestAlreadyCompletedException


_GDPR_DEADLINE_DAYS = 30


@dataclass
class DataSubjectRequest(AggregateRoot):
    """Корень агрегата запроса субъекта данных GDPR/CCPA (Security BC)."""

    user_id: Id = field(default_factory=Id.generate)
    request_type: DataSubjectRequestType = DataSubjectRequestType.EXPORT
    status: DataSubjectRequestStatus = DataSubjectRequestStatus.PENDING
    description: str | None = None
    rejection_reason: str | None = None
    assigned_to: Id | None = None
    export_file_path: str | None = None
    export_file_expires_at: datetime | None = None
    requested_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    completed_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create(cls, user_id: Id, request_type: DataSubjectRequestType, description: str | None = None) -> DataSubjectRequest:
        req = cls(user_id=user_id, request_type=request_type, description=description)
        req._register_event(
            DataSubjectRequestCreated(request_id=str(req.id), user_id=str(user_id), request_type=request_type)
        )
        return req

    def _assert_not_completed(self) -> None:
        if self.status in (DataSubjectRequestStatus.COMPLETED, DataSubjectRequestStatus.REJECTED):
            raise DataSubjectRequestAlreadyCompletedException()

    def assign(self, assigned_to: Id) -> None:
        self._assert_not_completed()
        self.assigned_to = assigned_to
        self.updated_at = datetime.now(tz=timezone.utc)

    def start_processing(self) -> None:
        self._assert_not_completed()
        if self.status != DataSubjectRequestStatus.PENDING:
            return
        self.status = DataSubjectRequestStatus.IN_PROGRESS
        self.updated_at = datetime.now(tz=timezone.utc)

    def complete_export(self, file_path: str, expires_at: datetime) -> None:
        self._assert_not_completed()
        self.status = DataSubjectRequestStatus.COMPLETED
        self.export_file_path = file_path
        self.export_file_expires_at = expires_at
        self.completed_at = datetime.now(tz=timezone.utc)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(DataSubjectRequestCompleted(request_id=str(self.id)))

    def complete_deletion(self) -> None:
        self._assert_not_completed()
        self.status = DataSubjectRequestStatus.COMPLETED
        self.completed_at = datetime.now(tz=timezone.utc)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(DataSubjectRequestCompleted(request_id=str(self.id)))

    def complete(self) -> None:
        self._assert_not_completed()
        self.status = DataSubjectRequestStatus.COMPLETED
        self.completed_at = datetime.now(tz=timezone.utc)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(DataSubjectRequestCompleted(request_id=str(self.id)))

    def reject(self, reason: str) -> None:
        self._assert_not_completed()
        self.status = DataSubjectRequestStatus.REJECTED
        self.rejection_reason = reason
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(DataSubjectRequestRejected(request_id=str(self.id), reason=reason))

    def is_expired(self) -> bool:
        deadline = self.requested_at + timedelta(days=_GDPR_DEADLINE_DAYS)
        return datetime.now(tz=timezone.utc) > deadline and self.status not in (DataSubjectRequestStatus.COMPLETED, DataSubjectRequestStatus.REJECTED)
