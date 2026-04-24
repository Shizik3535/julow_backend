from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_domain_event import BaseDomainEvent


@dataclass(frozen=True)
class BoardColumnAdded(BaseDomainEvent):
    """Колонка добавлена."""

    project_id: str = ""
    column_id: str = ""
    name: str = ""


@dataclass(frozen=True)
class BoardColumnRemoved(BaseDomainEvent):
    """Колонка удалена."""

    project_id: str = ""
    column_id: str = ""


@dataclass(frozen=True)
class BoardColumnReordered(BaseDomainEvent):
    """Колонки переупорядочены."""

    project_id: str = ""


@dataclass(frozen=True)
class WIPLimitChanged(BaseDomainEvent):
    """WIP-лимит изменён."""

    project_id: str = ""
    column_id: str = ""


@dataclass(frozen=True)
class SwimlaneAdded(BaseDomainEvent):
    """Swimlane добавлена."""

    project_id: str = ""
    swimlane_id: str = ""


@dataclass(frozen=True)
class SwimlaneRemoved(BaseDomainEvent):
    """Swimlane удалена."""

    project_id: str = ""
    swimlane_id: str = ""


@dataclass(frozen=True)
class WorkflowStatusAdded(BaseDomainEvent):
    """Статус workflow добавлен."""

    project_id: str = ""
    status_id: str = ""
    name: str = ""
    category: str = ""


@dataclass(frozen=True)
class WorkflowStatusRemoved(BaseDomainEvent):
    """Статус workflow удалён."""

    project_id: str = ""
    status_id: str = ""


@dataclass(frozen=True)
class WorkflowTransitionAdded(BaseDomainEvent):
    """Переход workflow добавлен."""

    project_id: str = ""
    transition_id: str = ""


@dataclass(frozen=True)
class WorkflowTransitionRemoved(BaseDomainEvent):
    """Переход workflow удалён."""

    project_id: str = ""
    transition_id: str = ""


@dataclass(frozen=True)
class ProjectViewCreated(BaseDomainEvent):
    """Представление создано."""

    project_id: str = ""
    view_id: str = ""


@dataclass(frozen=True)
class ProjectViewUpdated(BaseDomainEvent):
    """Представление обновлено."""

    project_id: str = ""
    view_id: str = ""


@dataclass(frozen=True)
class ProjectViewDeleted(BaseDomainEvent):
    """Представление удалено."""

    project_id: str = ""
    view_id: str = ""


@dataclass(frozen=True)
class AutomationRuleCreated(BaseDomainEvent):
    """Правило автоматизации создано."""

    project_id: str = ""
    rule_id: str = ""


@dataclass(frozen=True)
class AutomationRuleUpdated(BaseDomainEvent):
    """Правило автоматизации обновлено."""

    project_id: str = ""
    rule_id: str = ""


@dataclass(frozen=True)
class AutomationRuleDeleted(BaseDomainEvent):
    """Правило автоматизации удалено."""

    project_id: str = ""
    rule_id: str = ""


@dataclass(frozen=True)
class AutomationRuleTriggered(BaseDomainEvent):
    """Правило автоматизации сработало."""

    project_id: str = ""
    rule_id: str = ""
    trigger_data: dict = field(default_factory=dict)
