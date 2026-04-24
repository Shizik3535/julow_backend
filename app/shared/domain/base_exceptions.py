from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id


class DomainException(Exception):
    """
    Базовое исключение предметной области.

    Все специфичные исключения домена должны наследоваться от этого класса.
    Позволяет отличать доменные ошибки от инфраструктурных
    и системных на верхних уровнях приложения.

    Атрибуты:
        message: Человекочитаемое описание ошибки.

    Пример:
        class InsufficientFunds(DomainException):
            def __init__(self, balance: Decimal, amount: Decimal) -> None:
                super().__init__(
                    f"Недостаточно средств: баланс {balance}, списание {amount}"
                )
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
