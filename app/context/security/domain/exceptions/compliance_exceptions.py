from __future__ import annotations

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class SecurityPolicyNotFoundException(EntityNotFoundException):
    def __init__(self, id: object) -> None:
        super().__init__(entity_type="SecurityPolicy", id=id)


class ComplianceConfigNotFoundException(EntityNotFoundException):
    def __init__(self, id: object) -> None:
        super().__init__(entity_type="ComplianceConfig", id=id)


class ComplianceViolationException(BusinessRuleViolationException):
    def __init__(self, detail: str = "") -> None:
        super().__init__(rule="Compliance", message=f"Нарушение compliance{f': {detail}' if detail else ''}")


class DataResidencyViolationException(BusinessRuleViolationException):
    def __init__(self) -> None:
        super().__init__(rule="DataResidency", message="Нарушение data residency")


class InvalidDataResidencyException(BusinessRuleViolationException):
    def __init__(self, detail: str = "") -> None:
        super().__init__(rule="ValidDataResidency", message=f"Некорректная конфигурация data residency{f': {detail}' if detail else ''}")


class CannotExportDataException(DomainException):
    def __init__(self) -> None:
        super().__init__("Нельзя экспортировать данные")


class CannotDeleteDataException(DomainException):
    def __init__(self) -> None:
        super().__init__("Нельзя удалить данные")
