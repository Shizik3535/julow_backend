from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id

TAggregate = TypeVar("TAggregate", bound=AggregateRoot)


class RepositoryPort(ABC, Generic[TAggregate]):
    """
    Порт (интерфейс) репозитория — RepositoryPort[TAggregate].

    Репозиторий абстрагирует доступ к хранилищу агрегатов.
    Application-слой зависит от этого порта, infrastructure-слой реализует.

    Правила DDD:
        - Репозиторий работает только с Aggregate Root
        - Один репозиторий = один тип агрегата
        - Репозиторий гарантирует консистентность агрегата при сохранении

    Параметры типа:
        TAggregate: Тип агрегата, с которым работает репозиторий.

    Пример:
        class OrderRepository(RepositoryPort[Order]):
            async def get_by_customer(self, customer_id: Id) -> list[Order]: ...
    """

    @abstractmethod
    async def get_by_id(self, id: Id) -> TAggregate | None:
        """
        Найти агрегат по идентификатору.

        Аргументы:
            id: Идентификатор агрегата.

        Возвращает:
            Агрегат или None, если не найден.
        """

    @abstractmethod
    async def get_all(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[TAggregate]:
        """
        Получить список агрегатов с опциональной фильтрацией.

        Аргументы:
            offset: Смещение для пагинации.
            limit: Максимальное количество записей.
            filters: Словарь фильтров {поле: значение}.

        Возвращает:
            Список агрегатов.
        """

    @abstractmethod
    async def get_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[TAggregate], int]:
        """
        Получить страницу агрегатов с общим количеством.

        Аргументы:
            page: Номер страницы (1-based).
            page_size: Размер страницы.
            filters: Словарь фильтров {поле: значение}.

        Возвращает:
            Кортеж (список агрегатов страницы, общее количество).
        """

    @abstractmethod
    async def add(self, aggregate: TAggregate) -> TAggregate:
        """
        Добавить новый агрегат в хранилище.

        Аргументы:
            aggregate: Агрегат для добавления.

        Возвращает:
            Добавленный агрегат (с назначенным ID, если применимо).
        """

    @abstractmethod
    async def update(self, aggregate: TAggregate) -> TAggregate:
        """
        Обновить существующий агрегат в хранилище.

        Аргументы:
            aggregate: Агрегат с обновлённым состоянием.

        Возвращает:
            Обновлённый агрегат.
        """

    @abstractmethod
    async def delete(self, id: Id) -> None:
        """
        Удалить агрегат из хранилища.

        Аргументы:
            id: Идентификатор агрегата для удаления.
        """


class SoftDeleteRepositoryPort(RepositoryPort[TAggregate]):
    """
    Порт репозитория с поддержкой мягкого удаления.

    Расширяет RepositoryPort методами soft_delete и restore.
    Применяется для агрегатов, которые поддерживают
    логическое удаление (корзину) вместо физического.

    ORM-модель такого агрегата должна иметь колонку soft_delete_at.

    Пример:
        class OrderRepository(SoftDeleteRepositoryPort[Order]):
            async def soft_delete(self, id: Id) -> None: ...
            async def restore(self, id: Id) -> None: ...
    """

    @abstractmethod
    async def soft_delete(self, id: Id) -> None:
        """
        Поместить агрегат в корзину (soft delete).

        Устанавливает soft_delete_at в текущее время.
        Агрегат остаётся в хранилище, но считается удалённым.

        Аргументы:
            id: Идентификатор агрегата.
        """

    @abstractmethod
    async def restore(self, id: Id) -> None:
        """
        Восстановить агрегат из корзины.

        Сбрасывает soft_delete_at в None.
        Агрегат снова считается активным.

        Аргументы:
            id: Идентификатор агрегата.
        """
