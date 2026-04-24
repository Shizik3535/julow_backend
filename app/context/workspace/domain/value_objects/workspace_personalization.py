from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.url_vo import Url
from app.context.workspace.domain.value_objects.workspace_branding import WorkspaceBranding


@dataclass(frozen=True)
class WorkspacePersonalization(ValueObject):
    """
    Группа настроек персонализации workspace.

    Атрибуты:
        color: Акцентный цвет (Color из shared kernel).
        icon_url: URL иконки.
        display_name: Отображаемое имя.
        description: Описание.
        branding: Настройки брендинга.
    """

    color: Color | None = None
    icon_url: Url | None = None
    display_name: str | None = None
    description: str | None = None
    branding: WorkspaceBranding | None = None
