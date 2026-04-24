from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.value_objects.url_vo import Url


@dataclass(frozen=True)
class WorkspaceBranding(ValueObject):
    """
    Группа настроек брендинга workspace.

    Атрибуты:
        logo_url: URL логотипа.
        cover_image_url: URL обложки.
        custom_css: Пользовательский CSS.
    """

    logo_url: Url | None = None
    cover_image_url: Url | None = None
    custom_css: str | None = None
