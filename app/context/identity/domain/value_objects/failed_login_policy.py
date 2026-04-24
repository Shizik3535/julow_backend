from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException
from app.context.identity.domain.value_objects.lockout_threshold import LockoutThreshold


@dataclass(frozen=True)
class FailedLoginPolicy(ValueObject):
    """
    Value Object для политики блокировки при неудачных попытках входа.

    Содержит список порогов блокировки, отсортированных по возрастанию
    failed_attempts. Прогрессивная блокировка: каждый следующий порог
    может увеличивать длительность блокировки.

    Атрибуты:
        thresholds: Список порогов блокировки (от меньшего к большему).
    """

    thresholds: list[LockoutThreshold] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.thresholds:
            raise ValidationException(
                field="thresholds",
                message="Политика должна содержать хотя бы один порог блокировки",
            )
        sorted_thresholds = sorted(self.thresholds, key=lambda t: t.failed_attempts)
        object.__setattr__(self, "thresholds", sorted_thresholds)

    def get_threshold_for_attempts(self, failed_attempts: int) -> LockoutThreshold | None:
        """
        Возвращает подходящий порог для текущего количества неудачных попыток.

        Аргументы:
            failed_attempts: Текущее количество неудачных попыток.

        Возвращает:
            Порог блокировки или None, если лимит не достигнут.
        """
        result = None
        for threshold in self.thresholds:
            if failed_attempts >= threshold.failed_attempts:
                result = threshold
        return result
