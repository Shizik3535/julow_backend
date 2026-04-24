from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class StartPage(ValueObject):
    """
    Идентификатор стартовой страницы.

    Новые разделы приложения появляются часто. Строка с валидацией
    на app-слое (проверка что страница существует) вместо enum.

    Атрибуты:
        value: Идентификатор страницы (например "dashboard", "my_tasks").
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValidationException(
                field="start_page",
                message="Идентификатор стартовой страницы не может быть пустым",
            )

    def __str__(self) -> str:
        return self.value
