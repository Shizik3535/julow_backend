from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.url_vo import Url
from app.shared.domain.exceptions import ValidationException


@dataclass
class SocialLink(BaseEntity):
    """
    Социальная ссылка пользователя.

    Атрибуты:
        platform: Название платформы (например "github", "linkedin").
        url: URL ссылки.
        display_name: Отображаемое имя (опционально).
    """

    platform: str = ""
    url: Url = field(default_factory=lambda: Url("https://example.com"))
    display_name: str | None = None

    def __post_init__(self) -> None:
        if not self.platform.strip():
            raise ValidationException(
                field="platform",
                message="Название платформы не может быть пустым",
            )
