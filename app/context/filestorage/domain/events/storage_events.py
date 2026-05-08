from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_domain_event import BaseDomainEvent


@dataclass(frozen=True)
class StorageQuotaApproaching(BaseDomainEvent):
    """Квота хранилища приближается (≥90%)."""

    storage_id: str = ""
    used_percent: int = 0
