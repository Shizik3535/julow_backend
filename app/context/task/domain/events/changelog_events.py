from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_domain_event import BaseDomainEvent


@dataclass(frozen=True)
class ChangelogEntryCreated(BaseDomainEvent):
    """Запись истории изменений создана."""

    task_id: str = ""
    field_name: str = ""
