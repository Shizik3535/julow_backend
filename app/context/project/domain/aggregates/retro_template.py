from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.context.project.domain.value_objects.retro_section import RetroSection
from app.context.project.domain.events.retro_template_events import (
    RetroTemplateCreated,
    RetroTemplateUpdated,
    RetroTemplateDeleted,
)
from app.context.project.domain.exceptions.project_role_exceptions import (
    CannotDeleteSystemRoleException,
)


@dataclass
class RetroTemplate(AggregateRoot):
    """
    Корень агрегата шаблона ретроспективы (Project BC).

    Предустановленные шаблоны (classic, 4ls, start_stop_continue, mad_sad_glad)
    с is_system=True. Кастомные шаблоны создаются админами проекта.

    Атрибуты:
        name: Название шаблона.
        sections: Секции шаблона (VOs).
        is_system: Является ли шаблон системным.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    name: str = ""
    sections: list[RetroSection] = field(default_factory=list)
    is_system: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create_system(cls, name: str, sections: list[RetroSection]) -> RetroTemplate:
        """Создаёт системный шаблон."""
        template = cls(name=name, sections=sections, is_system=True)
        template._register_event(RetroTemplateCreated(template_name=name))
        return template

    @classmethod
    def create_custom(cls, name: str, sections: list[RetroSection]) -> RetroTemplate:
        """Создаёт кастомный шаблон."""
        template = cls(name=name, sections=sections, is_system=False)
        template._register_event(RetroTemplateCreated(template_name=name))
        return template

    def update(self, sections: list[RetroSection] | None = None) -> None:
        if sections is not None:
            self.sections = sections
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(RetroTemplateUpdated(template_name=self.name))

    def assert_deletable(self) -> None:
        if self.is_system:
            raise CannotDeleteSystemRoleException(role_name=self.name)

    def mark_deleted(self) -> None:
        self.assert_deletable()
        self._register_event(RetroTemplateDeleted(template_name=self.name))
