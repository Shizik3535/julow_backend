from __future__ import annotations

from enum import Enum


class IpRuleType(Enum):
    WHITELIST = "whitelist"
    BLACKLIST = "blacklist"
