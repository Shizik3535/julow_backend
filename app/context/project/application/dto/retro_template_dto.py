from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class RetroTemplateDTO:
    """DTO шаблона ретроспективы."""

    id: str = ""
    name: str = ""
    sections: list[dict[str, Any]] = field(default_factory=list)
    is_system: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class RetroTemplateListDTO:
    """Список шаблонов ретроспектив."""

    items: list[RetroTemplateDTO] = field(default_factory=list)
    total: int = 0
