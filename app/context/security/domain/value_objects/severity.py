from __future__ import annotations

from enum import Enum


class Severity(Enum):
    INFO = "info"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"
