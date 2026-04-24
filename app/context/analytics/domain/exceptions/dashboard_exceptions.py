from __future__ import annotations

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class DashboardNotFoundException(EntityNotFoundException):
    def __init__(self, id: object) -> None:
        super().__init__(entity_type="Dashboard", id=id)


class WidgetNotFoundException(EntityNotFoundException):
    def __init__(self, id: object) -> None:
        super().__init__(entity_type="Widget", id=id)


class DashboardShareNotFoundException(EntityNotFoundException):
    def __init__(self, id: object) -> None:
        super().__init__(entity_type="DashboardShare", id=id)


class DashboardTemplateNotFoundException(EntityNotFoundException):
    def __init__(self, id: object) -> None:
        super().__init__(entity_type="DashboardTemplate", id=id)


class CannotDeleteSystemTemplateException(BusinessRuleViolationException):
    def __init__(self, name: str = "") -> None:
        super().__init__(rule="SystemTemplateCannotBeDeleted", message=f"Нельзя удалить системный шаблон{f': {name}' if name else ''}")


class DuplicateShareException(BusinessRuleViolationException):
    def __init__(self) -> None:
        super().__init__(rule="UniqueShare", message="Шаринг уже существует для этого пользователя")


class CannotShareWithSelfException(BusinessRuleViolationException):
    def __init__(self) -> None:
        super().__init__(rule="CannotShareWithSelf", message="Нельзя расшарить с самим собой")
