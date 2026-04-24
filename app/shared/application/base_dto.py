from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class BaseDTO(BaseModel):
    """
    Базовый DTO (Data Transfer Object).

    DTO — объект для передачи данных между слоями приложения.
    Не содержит бизнес-логики, только данные.

    Используется:
        - Как результат QueryHandler (возврат данных)
        - Как входной параметр CommandHandler (входные данные)
        - В presentation-слое для формирования ответов API

    Правила:
        - DTO — Pydantic модель (валидация, сериализация)
        - Не содержит методов бизнес-логики
        - Не зависит от доменных объектов напрямую
        - Имена полей соответствуют API-контракту
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
