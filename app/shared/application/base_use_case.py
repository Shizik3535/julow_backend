from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.core.logging import get_logger

TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


class BaseUseCase(ABC, Generic[TInput, TOutput]):
    """
    Базовый Use Case (вариант использования).

    Инкапсулирует одну бизнес-операцию приложения.
    Является общим предком для CommandHandler, QueryHandler
    и EventHandler, обеспечивая единый интерфейс execute().

    Параметры типа:
        TInput: Тип входных данных (Command, Query или Event).
        TOutput: Тип возвращаемого результата (DTO или None).

    Атрибуты:
        _logger: Structlog-логгер, привязанный к имени класса.

    Правила:
        - Один UseCase = одна бизнес-операция
        - Не содержит бизнес-логики — делегирует домену
        - Оркестрирует работу: загружает агрегат, вызывает метод, сохраняет
        - Возвращает DTO, а не доменный объект

    Пример:
        class CreateTaskUseCase(BaseUseCase[CreateTaskCommand, TaskDTO]):
            async def execute(self, command: CreateTaskCommand) -> TaskDTO:
                task = Task.create(command.title, command.description)
                await self.task_repo.add(task)
                return TaskDTO.model_validate(task)
    """

    def __init__(self) -> None:
        self._logger = get_logger(self.__class__.__name__)

    @abstractmethod
    async def execute(self, input_: TInput) -> TOutput:
        """
        Выполнить вариант использования.

        Аргументы:
            input_: Входные данные (Command, Query или Event).

        Возвращает:
            Результат выполнения (DTO или None).
        """
