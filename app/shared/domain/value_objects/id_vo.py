from __future__ import annotations

from uuid import UUID, uuid4
from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject


@dataclass(frozen=True)
class Id(ValueObject):
    """
    Тип идентификатора на основе UUID.

    Используется как тип ID для всех Entity и AggregateRoot.
    Value Object — неизменяем, сравнивается по значению.

    Атрибуты:
        value: UUID значение идентификатора.

    Пример:
        entity_id = Id.generate()
        same_id = Id(entity_id.value)
    """

    value: UUID

    @classmethod
    def generate(cls) -> Id:
        """Генерирует новый случайный Id."""
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, raw: str) -> Id:
        """
        Создаёт Id из строкового представления UUID.

        Аргументы:
            raw: Строка в формате UUID.

        Raises:
            ValueError: Если строка не является валидным UUID.
        """
        return cls(value=UUID(raw))

    def __str__(self) -> str:
        return str(self.value)

