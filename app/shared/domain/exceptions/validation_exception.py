from __future__ import annotations

from app.shared.domain.base_exceptions import DomainException


class ValidationException(DomainException):
    """
    Исключение ошибки валидации.

    Выбрасывается, когда значение не проходит проверку
    на уровне предметной области (Value Object, Entity).

    Атрибуты:
        field: Имя поля, в котором обнаружена ошибка.
        message: Человекочитаемое описание ошибки валидации.

    Пример:
        raise ValidationException(
            field="email",
            message="Некорректный формат email",
        )
    """

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        super().__init__(message)
