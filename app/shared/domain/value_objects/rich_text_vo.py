from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.value_objects.rich_text_format import RichTextFormat


@dataclass(frozen=True)
class RichText(ValueObject):
    """
    Value Object для форматированного текста.

    Хранит содержимое и формат разметки.

    Атрибуты:
        content: Текстовое содержимое.
        format: Формат разметки (MARKDOWN или WYSIWYG).
    """

    content: str = ""
    format: RichTextFormat = RichTextFormat.MARKDOWN

    def __str__(self) -> str:
        return self.content
