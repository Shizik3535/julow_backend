from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class TaskTemplateAlreadyExistsException(ApplicationException):
    """Шаблон задачи с таким именем уже существует."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Шаблон задачи '{name}' уже существует")
        self.name = name
