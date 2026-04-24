from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine


class BackgroundTasksPort(ABC):
    """
    Порт фоновых задач (Background Tasks Port).

    Определяет интерфейс для запуска задач в фоне,
    вне основного потока обработки запроса.
    Infrastructure-слой реализует этот порт (Celery, ARQ, asyncio и т.д.).

    Правила:
        - Задача выполняется асинхронно, не блокируя вызывающий код
        - Вызывающий код не получает результат задачи напрямую
        - Ошибки в фоновой задаче не должны ломать основной поток
    """

    @abstractmethod
    async def run(
        self,
        func: Callable[..., Coroutine[Any, Any, Any]],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Запустить функцию в фоне.

        Аргументы:
            func: Асинхронная функция для выполнения.
            *args: Позиционные аргументы функции.
            **kwargs: Именованные аргументы функции.
        """

    @abstractmethod
    async def run_delayed(
        self,
        func: Callable[..., Coroutine[Any, Any, Any]],
        delay_seconds: float,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Запустить функцию в фоне с задержкой.

        Аргументы:
            func: Асинхронная функция для выполнения.
            delay_seconds: Задержка перед запуском (в секундах).
            *args: Позиционные аргументы функции.
            **kwargs: Именованные аргументы функции.
        """
