from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, fields


@dataclass(frozen=True)
class ValueObject(ABC):
    """
    Базовый Value Object (объект-значение).

    Value Object определяется своими атрибутами, а не идентичностью.
    Два Value Object с одинаковыми атрибутами считаются равными.
    Value Object неизменяем (immutable) — вместо изменения создаётся новый.

    Правила DDD:
        - Нет идентичности (сравнение по значениям)
        - Неизменяемость — после создания состояние не меняется
        - Может использоваться как атрибут Entity или другого Value Object
        - Заменяемость — два VO с одинаковыми значениями взаимозаменяемы

    frozen=True обеспечивает:
        - Автоматическое сравнение по значениям (__eq__)
        - Автоматический хеш (__hash__)
        - Запрет изменения полей после создания (FrozenInstanceError)
        - Автоматический __repr__

    """

    def clone(self, **overrides: object) -> ValueObject:
        """
        Создаёт копию Value Object с переопределёнными атрибутами.

        Аргументы:
            overrides: Атрибуты, которые нужно заменить в копии.
        """
        current = {f.name: getattr(self, f.name) for f in fields(self)}
        current.update(overrides)
        return type(self)(**current)
