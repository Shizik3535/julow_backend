from __future__ import annotations

from abc import abstractmethod
from typing import Generic, TypeVar

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_use_case import BaseUseCase

TCommand = TypeVar("TCommand", bound=BaseCommand)
TResult = TypeVar("TResult")


class BaseCommandHandler(BaseUseCase[TCommand, TResult], Generic[TCommand, TResult]):
    """
    Базовый обработчик команды (Command Handler).

    Принимает команду и выполняет соответствующую бизнес-операцию.
    Оркестрирует: загрузка агрегата → вызов метода → сохранение → диспетчеризация событий.

    Параметры типа:
        TCommand: Тип обрабатываемой команды.
        TResult: Тип возвращаемого результата (или None).

    Связь с BaseUseCase:
        - Наследует execute() и логгер от BaseUseCase
        - execute() делегирует вызов в handle()
        - Конкретный обработчик реализует только handle()

    Правила:
        - Один CommandHandler = одна команда
        - Не содержит бизнес-логики — делегирует агрегату
        - Может возвращать результат (ID созданной сущности, DTO и т.д.)

    Пример:
        class CreateTaskHandler(BaseCommandHandler[CreateTaskCommand, TaskDTO]):
            def __init__(self, task_repo: TaskRepository) -> None:
                super().__init__()
                self.task_repo = task_repo

            async def handle(self, command: CreateTaskCommand) -> TaskDTO:
                task = Task.create(command.title, command.description)
                await self.task_repo.add(task)
                return TaskDTO.model_validate(task)
    """

    async def execute(self, command: TCommand) -> TResult:
        """
        Точка входа для обработки команды.

        Делегирует выполнение в handle().

        Аргументы:
            command: Команда для выполнения.

        Возвращает:
            Результат выполнения (опционально, например ID).
        """
        return await self.handle(command)

    @abstractmethod
    async def handle(self, command: TCommand) -> TResult:
        """
        Обработать команду.

        Аргументы:
            command: Команда для выполнения.

        Возвращает:
            Результат выполнения (опционально, например ID).
        """
