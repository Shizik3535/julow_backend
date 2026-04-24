from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.value_objects.url_vo import Url


@dataclass(frozen=True)
class OrgBranding(ValueObject):
    """
    Группа настроек брендинга организации.

    Атрибуты:
        logo_url: URL логотипа.
        favicon_url: URL фавикона.
        custom_css: Пользовательский CSS.
        login_message: Сообщение на странице входа.
    """

    logo_url: Url | None = None
    favicon_url: Url | None = None
    custom_css: str | None = None
    login_message: str | None = None
