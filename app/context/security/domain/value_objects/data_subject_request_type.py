from __future__ import annotations

from enum import Enum


class DataSubjectRequestType(Enum):
    EXPORT = "export"
    DELETION = "deletion"
    CORRECTION = "correction"
    RESTRICTION = "restriction"
    OBJECTION = "objection"
