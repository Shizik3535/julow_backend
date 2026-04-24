from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_value_object import ValueObject
from app.context.project.domain.value_objects.custom_field_type import CustomFieldType


@dataclass(frozen=True)
class CustomFieldDefinition(ValueObject):
    """
    Определение кастомного поля проекта.

    Атрибуты:
        name: Имя поля (уникальное в рамках проекта).
        field_type: Тип поля.
        is_required: Обязательное ли поле.
        options: Варианты для SELECT/MULTI_SELECT.
        default_value: Значение по умолчанию.
        description: Описание поля.
    """

    name: str
    field_type: CustomFieldType = CustomFieldType.TEXT
    is_required: bool = False
    options: list[str] | None = None
    default_value: str | None = None
    description: str | None = None
