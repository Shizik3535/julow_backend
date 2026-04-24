from __future__ import annotations

from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class DataSubjectRequestNotFoundException(EntityNotFoundException):
    def __init__(self, id: object) -> None:
        super().__init__(entity_type="DataSubjectRequest", id=id)


class DataSubjectRequestAlreadyCompletedException(BusinessRuleViolationException):
    def __init__(self) -> None:
        super().__init__(rule="RequestNotAlreadyCompleted", message="Запрос уже выполнен")


class IpRuleNotFoundException(EntityNotFoundException):
    def __init__(self, id: object) -> None:
        super().__init__(entity_type="IpRule", id=id)


class DuplicateIpRuleException(BusinessRuleViolationException):
    def __init__(self, ip_range: str = "") -> None:
        super().__init__(rule="UniqueIpRule", message=f"Правило для этого IP диапазона уже существует{f': {ip_range}' if ip_range else ''}")


class InvalidIpRangeException(BusinessRuleViolationException):
    def __init__(self, ip_range: str = "") -> None:
        super().__init__(rule="ValidIpRange", message=f"Некорректный CIDR диапазон{f': {ip_range}' if ip_range else ''}")


class BackupScheduleNotFoundException(EntityNotFoundException):
    def __init__(self, id: object) -> None:
        super().__init__(entity_type="BackupSchedule", id=id)


class BackupNotFoundException(EntityNotFoundException):
    def __init__(self, id: object) -> None:
        super().__init__(entity_type="BackupRecord", id=id)


class EncryptionConfigNotFoundException(EntityNotFoundException):
    def __init__(self, id: object) -> None:
        super().__init__(entity_type="EncryptionConfig", id=id)
