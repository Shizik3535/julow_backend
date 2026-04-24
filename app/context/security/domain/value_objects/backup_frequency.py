from __future__ import annotations

from enum import Enum


class BackupFrequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
