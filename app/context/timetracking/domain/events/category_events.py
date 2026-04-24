from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_domain_event import BaseDomainEvent


@dataclass(frozen=True)
class ActivityCategoryCreated(BaseDomainEvent):
    """Категория деятельности создана."""

    category_id: str = ""
    name: str = ""


@dataclass(frozen=True)
class ActivityCategoryDeleted(BaseDomainEvent):
    """Категория деятельности удалена."""

    category_id: str = ""
