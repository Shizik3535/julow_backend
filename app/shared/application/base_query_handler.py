from __future__ import annotations

from abc import abstractmethod
from typing import Generic, TypeVar

from app.shared.application.base_dto import BaseDTO
from app.shared.application.base_query import BaseQuery
from app.shared.application.base_use_case import BaseUseCase

TQuery = TypeVar("TQuery", bound=BaseQuery)
TResult = TypeVar("TResult", bound=BaseDTO)


class BaseQueryHandler(BaseUseCase[TQuery, TResult], Generic[TQuery, TResult]):
    """
    Базовый обработчик запроса (Query Handler).

    Принимает запрос и возвращает данные (DTO / проекцию).
    Не изменяет состояние домена — только чтение.

    Параметры типа:
        TQuery: Тип обрабатываемого запроса.
        TResult: Тип возвращаемого результата (BaseDTO или наследник).

    Связь с BaseUseCase:
        - Наследует execute() и логгер от BaseUseCase
        - execute() делегирует вызов в handle()
        - Конкретный обработчик реализует только handle()

    Правила:
        - Один QueryHandler = один запрос
        - Не содержит бизнес-логики
        - Может использовать отдельную модель чтения (CQRS read model)
        - Возвращает DTO, а не доменный объект

    Пример:
        class GetTaskByIdHandler(BaseQueryHandler[GetTaskByIdQuery, TaskDTO]):
            def __init__(self, task_repo: TaskRepository) -> None:
                super().__init__()
                self.task_repo = task_repo

            async def handle(self, query: GetTaskByIdQuery) -> TaskDTO:
                task = await self.task_repo.get_by_id(query.task_id)
                if task is None:
                    raise EntityNotFoundException(f"Task {query.task_id} not found")
                return TaskDTO.model_validate(task)
    """

    async def execute(self, query: TQuery) -> TResult:
        """
        Точка входа для обработки запроса.

        Делегирует выполнение в handle().

        Аргументы:
            query: Запрос для выполнения.

        Возвращает:
            Результат чтения (DTO / проекция).
        """
        return await self.handle(query)

    @abstractmethod
    async def handle(self, query: TQuery) -> TResult:
        """
        Обработать запрос.

        Аргументы:
            query: Запрос для выполнения.

        Возвращает:
            Результат чтения (DTO / проекция).
        """
