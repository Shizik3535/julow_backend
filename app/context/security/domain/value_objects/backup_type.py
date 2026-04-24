from __future__ import annotations

from enum import Enum


class BackupType(Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    SNAPSHOT = "snapshot"
