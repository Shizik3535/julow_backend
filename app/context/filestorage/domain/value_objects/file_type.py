from __future__ import annotations

from enum import Enum


class FileType(Enum):
    """
    Тип файла.

    Определяется по MIME-типу на app-слое. Новые типы = значение enum.

    Значения:
        IMAGE: Изображение
        VIDEO: Видео
        PDF: PDF документ
        OFFICE: Офисный документ
        ARCHIVE: Архив
        AUDIO: Аудио
        CODE: Исходный код
        FONT: Шрифт
        SPREADSHEET: Таблица
        PRESENTATION: Презентация
        THREE_D_MODEL: 3D модель
        OTHER: Другое (fallback)
    """

    IMAGE = "image"
    VIDEO = "video"
    PDF = "pdf"
    OFFICE = "office"
    ARCHIVE = "archive"
    AUDIO = "audio"
    CODE = "code"
    FONT = "font"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    THREE_D_MODEL = "3d_model"
    OTHER = "other"
