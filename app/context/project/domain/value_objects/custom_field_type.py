from __future__ import annotations

from enum import Enum


class CustomFieldType(Enum):
    """
    Тип кастомного поля.

    Значения:
        TEXT: Текстовое поле
        NUMBER: Числовое поле
        DATE: Дата
        SELECT: Выбор из списка
        MULTI_SELECT: Множественный выбор
        URL: URL-ссылка
        USER: Пользователь
        CHECKBOX: Флажок
    """

    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    URL = "url"
    USER = "user"
    CHECKBOX = "checkbox"
