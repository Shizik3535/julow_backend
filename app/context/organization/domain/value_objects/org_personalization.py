from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.value_objects.url_vo import Url
from app.context.organization.domain.value_objects.accent_color import AccentColor
from app.context.organization.domain.value_objects.org_branding import OrgBranding


@dataclass(frozen=True)
class OrgPersonalization(ValueObject):
    """
    Группа настроек персонализации организации.

    Атрибуты:
        color: Акцентный цвет.
        icon_url: URL иконки.
        display_name: Отображаемое имя.
        custom_domain: Кастомный домен.
        branding: Настройки брендинга.
    """

    color: AccentColor | None = None
    icon_url: Url | None = None
    display_name: str | None = None
    custom_domain: str | None = None
    branding: OrgBranding | None = None
