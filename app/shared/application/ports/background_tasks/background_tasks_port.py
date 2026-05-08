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

    @abstractmethod
    def send_task(
        self,
        name: str,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
        countdown: int | None = None,
        eta: Any = None,
        expires: int | None = None,
    ) -> Any:
        """
        Поставить именованную задачу в очередь воркеров.

        В отличие от ``run`` (передача функции по ссылке),
        ``send_task`` отправляет задачу по строковому имени, заранее
        зарегистрированному через ``register_task``. Это требуется,
        когда вызывающий код и обработчик живут в разных процессах
        (типичный сценарий с Celery worker'ами).

        Аргументы:
            name: Имя зарегистрированной задачи.
            args: Позиционные аргументы задачи.
            kwargs: Именованные аргументы задачи.
            countdown: Задержка перед выполнением (секунды).
            eta: Время выполнения (datetime).
            expires: Время истечения задачи (секунды).
        """
