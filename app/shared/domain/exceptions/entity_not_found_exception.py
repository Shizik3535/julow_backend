from __future__ import annotations

from app.shared.domain.base_exceptions import DomainException


class EntityNotFoundException(DomainException):
    """
    Исключение отсутствия сущности.

    Выбрасывается, когда сущность не найдена по идентификатору
    или другим критериям поиска.

    Атрибуты:
        entity_type: Тип сущности, которая не найдена.
        id: Идентификатор, по которому осуществлялся поиск.
        message: Человекочитаемое описание ошибки.

    Пример:
        raise EntityNotFoundException(
            entity_type="User",
            id=user_id,
        )
    """

    def __init__(self, entity_type: str, id: object, message: str | None = None) -> None:
        self.entity_type = entity_type
        self.id = id
        if message is None:
            message = f"{entity_type} с идентификатором {id} не найден(а)"
        super().__init__(message)
