from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.base_repository import RepositoryPort, SoftDeleteRepositoryPort
from app.shared.domain.exceptions.entity_not_found_exception import EntityNotFoundException
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper
from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel

logger = get_logger(__name__)

TAggregate = TypeVar("TAggregate", bound=AggregateRoot)
TORMModel = TypeVar("TORMModel", bound=BaseORMModel)


class SqlAlchemyRepository(RepositoryPort[TAggregate], Generic[TAggregate, TORMModel]):
    """
    Базовый репозиторий на основе SQLAlchemy async.

    Реализует Generic Repository Pattern с Data Mapper.
    Конкретные репозитории наследуют этот класс и указывают
    типы агрегата и ORM-модели.

    Параметры типа:
        TAggregate: Тип доменного агрегата.
        TORMModel: Тип ORM-модели.

    Аргументы конструктора:
        session: Async SQLAlchemy сессия.
        mapper: Data Mapper для преобразования Domain ↔ ORM.
        orm_model_class: Класс ORM-модели (для запросов).
    """

    def __init__(
        self,
        session: AsyncSession,
        mapper: BaseMapper[TAggregate, TORMModel],
        orm_model_class: type[TORMModel],
    ) -> None:
        self._session = session
        self._mapper = mapper
        self._orm_model_class = orm_model_class

    def _apply_filters(self, stmt: Any, filters: dict[str, Any] | None) -> Any:
        """Применить фильтры к SQLAlchemy запросу."""
        if not filters:
            return stmt
        for field, value in filters.items():
            col = getattr(self._orm_model_class, field, None)
            if col is not None:
                stmt = stmt.where(col == value)
        return stmt

    async def get_by_id(self, id: Id) -> TAggregate | None:
        uuid_value = self._mapper._map_uuid(id)
        stmt = select(self._orm_model_class).where(self._orm_model_class.id == uuid_value)
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model is None:
            logger.debug("Aggregate not found", id=str(uuid_value))
            return None
        return self._mapper.to_domain(orm_model)

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[TAggregate]:
        stmt = select(self._orm_model_class)
        stmt = self._apply_filters(stmt, filters)
        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        orm_models = result.scalars().all()
        return [self._mapper.to_domain(orm) for orm in orm_models]

    async def get_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[TAggregate], int]:
        # Count
        count_stmt = select(func.count()).select_from(self._orm_model_class)
        count_stmt = self._apply_filters(count_stmt, filters)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        # Data
        offset = (page - 1) * page_size
        stmt = select(self._orm_model_class)
        stmt = self._apply_filters(stmt, filters)
        stmt = stmt.offset(offset).limit(page_size)
        result = await self._session.execute(stmt)
        orm_models = result.scalars().all()
        aggregates = [self._mapper.to_domain(orm) for orm in orm_models]

        return aggregates, total

    async def add(self, aggregate: TAggregate) -> TAggregate:
        orm_model = self._mapper.to_orm(aggregate)
        self._session.add(orm_model)
        await self._session.flush()
        logger.debug("Aggregate added", id=str(aggregate.id))
        return aggregate

    async def update(self, aggregate: TAggregate) -> TAggregate:
        uuid_value = self._mapper._map_uuid(aggregate.id)
        stmt = select(self._orm_model_class).where(self._orm_model_class.id == uuid_value)
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model is None:
            raise EntityNotFoundException(
                entity_type=type(aggregate).__name__,
                id=aggregate.id,
            )

        updated_orm = self._mapper.to_orm(aggregate)
        for column in updated_orm.__table__.columns:
            col_name = column.name
            if col_name in ("id", "created_at"):
                continue
            setattr(orm_model, col_name, getattr(updated_orm, col_name, None))

        await self._session.flush()
        logger.debug("Aggregate updated", id=str(uuid_value))
        return aggregate

    async def delete(self, id: Id) -> None:
        uuid_value = self._mapper._map_uuid(id)
        stmt = select(self._orm_model_class).where(self._orm_model_class.id == uuid_value)
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model is not None:
            await self._session.delete(orm_model)
            await self._session.flush()
            logger.debug("Aggregate deleted", id=str(uuid_value))


class SoftDeleteSqlAlchemyRepository(
    SqlAlchemyRepository[TAggregate, TORMModel],
    SoftDeleteRepositoryPort[TAggregate],
):
    """
    Репозиторий с поддержкой мягкого удаления на основе SQLAlchemy async.

    Наследует SqlAlchemyRepository и реализует SoftDeleteRepositoryPort.
    ORM-модель должна иметь колонку soft_delete_at.

    Пример:
        class OrderRepository(SoftDeleteSqlAlchemyRepository[Order, OrderORM]):
            pass
    """

    async def soft_delete(self, id: Id) -> None:
        """Поместить агрегат в корзину (soft delete)."""
        uuid_value = self._mapper._map_uuid(id)
        stmt = select(self._orm_model_class).where(self._orm_model_class.id == uuid_value)
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model is not None:
            orm_model.soft_delete_at = datetime.now(tz=timezone.utc)
            await self._session.flush()
            logger.debug("Aggregate soft-deleted", id=str(uuid_value))

    async def restore(self, id: Id) -> None:
        """Восстановить агрегат из корзины."""
        uuid_value = self._mapper._map_uuid(id)
        stmt = select(self._orm_model_class).where(self._orm_model_class.id == uuid_value)
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model is not None:
            orm_model.soft_delete_at = None
            await self._session.flush()
            logger.debug("Aggregate restored", id=str(uuid_value))
