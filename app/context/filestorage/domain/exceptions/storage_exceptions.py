from __future__ import annotations

from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class StorageQuotaExceededException(BusinessRuleViolationException):
    """Квота хранилища превышена."""

    def __init__(self, max_bytes: int = 0, used_bytes: int = 0) -> None:
        super().__init__(
            rule="StorageQuota",
            message=f"Квота хранилища превышена (использовано: {used_bytes}, макс: {max_bytes})",
        )


class StorageNotFoundException(EntityNotFoundException):
    """Хранилище не найдено."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="Storage", id=id)
