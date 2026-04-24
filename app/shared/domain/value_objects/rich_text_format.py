from __future__ import annotations

from enum import Enum


class RichTextFormat(Enum):
    """
    Формат форматированного текста.

    Значения:
        MARKDOWN: Markdown-разметка
        WYSIWYG: WYSIWYG-редактор (визуальный)
    """

    MARKDOWN = "markdown"
    WYSIWYG = "wysiwyg"
