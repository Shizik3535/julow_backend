from __future__ import annotations

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class SecurityEventNotFoundException(EntityNotFoundException):
    def __init__(self, id: object) -> None:
        super().__init__(entity_type="SecurityEvent", id=id)


class SecurityIncidentNotFoundException(EntityNotFoundException):
    def __init__(self, id: object) -> None:
        super().__init__(entity_type="SecurityIncident", id=id)


class CannotResolveAlreadyResolvedEventException(BusinessRuleViolationException):
    def __init__(self) -> None:
        super().__init__(rule="EventNotAlreadyResolved", message="Событие уже разрешено")


class CannotModifyResolvedIncidentException(BusinessRuleViolationException):
    def __init__(self) -> None:
        super().__init__(rule="IncidentNotResolved", message="Нельзя изменить разрешённый инцидент")
