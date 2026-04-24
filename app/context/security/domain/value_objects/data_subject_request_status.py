from __future__ import annotations

from enum import Enum


class DataSubjectRequestStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
