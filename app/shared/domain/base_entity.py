from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field

from app.shared.domain.value_objects.id_vo import Id


@dataclass
class BaseEntity(ABC):
    """
    Базовая сущность (BaseEntity).

    Сущность определяется своей идентичностью (Id), а не атрибутами.
    Две сущности с одинаковым Id считаются одним и тем же объектом,
    даже если остальные атрибуты различаются.

    Правила DDD:
        - Имеет уникальную идентичность (Id)
        - Сравнение по идентичности, а не по значениям атрибутов
        - Изменяемость — состояние может меняться в течение жизненного цикла
        - Может содержать Value Objects как атрибуты

    Атрибуты:
        id: Уникальный идентификатор сущности.

    Пример:
        class User(BaseEntity):
            name: str
            email: Email
    """

    id: Id = field(default_factory=Id.generate)

    def __post_init__(self) -> None:
        """
        Хук инициализации dataclass'а.

        По умолчанию — no-op. Наследники могут переопределить его для валидации
        обязательных полей и вызывать `super().__post_init__()` в начале,
        чтобы не нарушать цепочку инициализации (см. Task, Project и т.д.).
        """
        return None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseEntity):
            return NotImplemented
        return type(self) is type(other) and self.id == other.id

    def __hash__(self) -> int:
        return hash((type(self), self.id))

    def __repr__(self) -> str:
        return f"{type(self).__name__}(id={self.id})"
