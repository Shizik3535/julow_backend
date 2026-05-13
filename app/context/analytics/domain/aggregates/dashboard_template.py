from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.exceptions import ValidationException
from app.shared.domain.value_objects.id_vo import Id
from app.context.analytics.domain.value_objects.widget_config import WidgetConfig
from app.context.analytics.domain.exceptions.dashboard_exceptions import CannotDeleteSystemTemplateException


@dataclass
class DashboardTemplate(AggregateRoot):
    """Корень агрегата шаблона дашборда (Analytics BC).

    ``workspace_id`` определяет область видимости шаблона:

    - системные шаблоны (``is_system=True``) — глобальные, поэтому
      ``workspace_id is None``;
    - пользовательские (``is_system=False``) — обязательно привязаны к
      конкретному workspace, который их создал; ``get_by_workspace`` в
      репозитории фильтрует именно по этому полю, чтобы избежать утечки
      шаблонов между workspace'ами.
    """

    name: str = ""
    description: str | None = None
    widget_configs: list[WidgetConfig] = field(default_factory=list)
    is_system: bool = False
    workspace_id: Id | None = None
    is_deleted: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    def __post_init__(self) -> None:
        # Конвенция кодовой базы (см. base_entity.BaseEntity.__post_init__):
        # подкласс начинает с super(), чтобы не пропустить будущие
        # инварианты, добавленные на уровне BaseEntity/AggregateRoot.
        super().__post_init__()
        # Системные шаблоны глобальны (None), кастомные — обязательно
        # привязаны к workspace. Несоответствие выявляем сразу, чтобы не
        # попасть в БД с состоянием, которое нельзя корректно отфильтровать.
        if self.is_system and self.workspace_id is not None:
            raise ValidationException(
                field="workspace_id",
                message="System dashboard template cannot belong to a workspace",
            )
        if not self.is_system and self.workspace_id is None:
            raise ValidationException(
                field="workspace_id",
                message="Custom dashboard template must belong to a workspace",
            )

    @classmethod
    def create_system(cls, name: str, widget_configs: list[WidgetConfig], description: str | None = None) -> DashboardTemplate:
        return cls(
            name=name,
            widget_configs=widget_configs,
            description=description,
            is_system=True,
            workspace_id=None,
        )

    @classmethod
    def create_custom(
        cls,
        name: str,
        widget_configs: list[WidgetConfig],
        workspace_id: Id,
        description: str | None = None,
    ) -> DashboardTemplate:
        return cls(
            name=name,
            widget_configs=widget_configs,
            description=description,
            is_system=False,
            workspace_id=workspace_id,
        )

    def update(self, name: str | None = None, description: str | None = None, widget_configs: list[WidgetConfig] | None = None) -> None:
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if widget_configs is not None:
            self.widget_configs = widget_configs
        self.updated_at = datetime.now(tz=timezone.utc)

    def assert_deletable(self) -> None:
        if self.is_system:
            raise CannotDeleteSystemTemplateException(name=self.name)

    def mark_deleted(self) -> None:
        self.assert_deletable()
        self.is_deleted = True
        self.updated_at = datetime.now(tz=timezone.utc)
