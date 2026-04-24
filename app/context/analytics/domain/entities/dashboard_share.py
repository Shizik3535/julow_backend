from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id
from app.context.analytics.domain.value_objects.share_access_level import ShareAccessLevel


@dataclass
class DashboardShare(BaseEntity):
    """Сущность шаринга дашборда."""

    user_id: Id = field(default_factory=Id.generate)
    access_level: ShareAccessLevel = ShareAccessLevel.VIEW
    shared_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
