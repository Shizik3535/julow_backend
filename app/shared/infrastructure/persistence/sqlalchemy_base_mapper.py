from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel

TAggregate = TypeVar("TAggregate", bound=AggregateRoot)
TORMModel = TypeVar("TORMModel", bound=BaseORMModel)


class BaseMapper(ABC, Generic[TAggregate, TORMModel]):
    """
    Базовый Data Mapper — преобразование Domain ↔ ORM.

    Разделяет доменную модель и модель хранения.
    Domain-слой не знает о структуре БД,
    Infrastructure-слой не знает о бизнес-логике.

    Параметры типа:
        TAggregate: Тип доменного агрегата.
        TORMModel: Тип ORM-модели.

    Правила:
        - Маппер отвечает только за преобразование данных
        - Маппер не содержит бизнес-логики
        - Один маппер = один тип агрегата
    """

    @abstractmethod
    def to_domain(self, orm_model: TORMModel) -> TAggregate:
        """
        Преобразовать ORM-модель в доменный агрегат.

        Аргументы:
            orm_model: ORM-модель из базы данных.

        Возвращает:
            Доменный агрегат.
        """

    @abstractmethod
    def to_orm(self, aggregate: TAggregate) -> TORMModel:
        """
        Преобразовать доменный агрегат в ORM-модель.

        Аргументы:
            aggregate: Доменный агрегат.

        Возвращает:
            ORM-модель для сохранения в БД.
        """

    def _map_id(self, value: uuid.UUID | str) -> Id:
        """Преобразует UUID/строку в доменный Id."""
        if isinstance(value, str):
            return Id.from_string(value)
        return Id(value=value)

    def _map_uuid(self, id: Id) -> uuid.UUID:
        """Преобразует доменный Id в UUID."""
        if isinstance(id.value, uuid.UUID):
            return id.value
        return uuid.UUID(str(id.value))
