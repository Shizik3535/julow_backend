from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_domain_event import BaseDomainEvent


@dataclass(frozen=True)
class TaskTemplateCreated(BaseDomainEvent):
    """Шаблон задачи создан."""

    template_name: str = ""


@dataclass(frozen=True)
class TaskTemplateUpdated(BaseDomainEvent):
    """Шаблон задачи обновлён."""

    template_name: str = ""


@dataclass(frozen=True)
class TaskTemplateDeleted(BaseDomainEvent):
    """Шаблон задачи удалён."""

    template_name: str = ""
