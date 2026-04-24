from __future__ import annotations

from app.shared.domain.base_exceptions import DomainException


class BusinessRuleViolationException(DomainException):
    """
    Исключение нарушения бизнес-правила.

    Выбрасывается, когда действие нарушает инвариант или бизнес-правило
    предметной области.

    Атрибуты:
        rule: Название нарушенного бизнес-правила.
        message: Человекочитаемое описание нарушения.

    Пример:
        raise BusinessRuleViolationException(
            rule="UniqueEmail",
            message="Email уже используется другим пользователем",
        )
    """

    def __init__(self, rule: str, message: str) -> None:
        self.rule = rule
        super().__init__(message)
