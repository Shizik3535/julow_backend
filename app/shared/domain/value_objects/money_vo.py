from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class Money(ValueObject):
    """
    Value Object для денежных сумм.

    Хранит сумму и валюту. Сумма не может быть отрицательной.
    Использует Decimal для точных вычислений.

    Атрибуты:
        amount: Сумма в формате Decimal.
        currency: Код валюты (ISO 4217, например "RUB", "USD").

    Пример:
        price = Money(Decimal("199.99"), "RUB")
    """

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise ValidationException(
                field="amount",
                message="Сумма должна быть типа Decimal",
            )
        if self.amount < 0:
            raise ValidationException(
                field="amount",
                message=f"Сумма не может быть отрицательной: {self.amount}",
            )
        normalized = self.currency.strip().upper()
        object.__setattr__(self, "currency", normalized)
        if len(normalized) != 3 or not normalized.isalpha():
            raise ValidationException(
                field="currency",
                message=f"Некорректный код валюты: {self.currency}",
            )

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"
