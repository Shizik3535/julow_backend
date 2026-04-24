from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CachePort(ABC):
    """
    Порт (интерфейс) для кэширования.

    Абстрагирует работу с кэшем (Redis, Memcached, in-memory и т.д.).
    Application-слой зависит от этого порта, infrastructure-слой реализует.

    Методы:
        get: Получить значение по ключу.
        set: Сохранить значение с опциональным TTL.
        delete: Удалить ключ.
        exists: Проверить существование ключа.
        clear: Очистить кэш по шаблону ключа.

    Правила:
        - Кэш — временное хранилище, данные могут быть удалены в любой момент
        - Все значения должны быть сериализуемы
    """

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """
        Получить значение из кэша по ключу.

        Аргументы:
            key: Ключ кэша.

        Возвращает:
            Значение или None, если ключ не найден.
        """

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        Сохранить значение в кэш.

        Аргументы:
            key: Ключ кэша.
            value: Значение для сохранения (должно быть сериализуемо).
            ttl: Время жизни в секундах (None — бессрочно).
        """

    @abstractmethod
    async def delete(self, key: str) -> None:
        """
        Удалить ключ из кэша.

        Аргументы:
            key: Ключ кэша.
        """

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Проверить существование ключа в кэше.

        Аргументы:
            key: Ключ кэша.

        Возвращает:
            True, если ключ существует.
        """

    @abstractmethod
    async def clear(self, pattern: str = "*") -> int:
        """
        Очистить кэш по шаблону ключа.

        Аргументы:
            pattern: Шаблон ключей (glob-синтаксис).

        Возвращает:
            Количество удалённых ключей.
        """
