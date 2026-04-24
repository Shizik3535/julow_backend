from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id
from app.context.security.domain.value_objects.ip_rule_type import IpRuleType


@dataclass
class IpRule(BaseEntity):
    ip_range: str = ""
    rule_type: IpRuleType = IpRuleType.WHITELIST
    description: str | None = None
    created_by: Id = field(default_factory=Id.generate)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
