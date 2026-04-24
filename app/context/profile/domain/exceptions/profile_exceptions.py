from __future__ import annotations

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException, ValidationException


class ProfileNotFoundException(EntityNotFoundException):
    """Профиль не найден."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="UserProfile", id=id)


class InvalidHotkeyException(ValidationException):
    """Некорректная комбинация клавиш или неизвестный action."""

    def __init__(self, detail: str = "") -> None:
        super().__init__(
            field="hotkey",
            message=f"Некорректная комбинация клавиш{': ' + detail if detail else ''}",
        )


class InvalidDateFormatException(ValidationException):
    """Некорректный паттерн формата даты."""

    def __init__(self, value: str) -> None:
        super().__init__(
            field="date_format",
            message=f"Некорректный паттерн формата даты: {value}",
        )
        self.value = value


class InvalidStartPageException(ValidationException):
    """Некорректный идентификатор стартовой страницы."""

    def __init__(self, value: str) -> None:
        super().__init__(
            field="start_page",
            message=f"Некорректный идентификатор стартовой страницы: {value}",
        )
        self.value = value


class DuplicatePinnedItemException(BusinessRuleViolationException):
    """Элемент уже закреплён."""

    def __init__(self, target_type: str, target_id: str) -> None:
        super().__init__(
            rule="UniquePinnedItem",
            message=f"Элемент {target_type}:{target_id} уже закреплён",
        )
        self.target_type = target_type
        self.target_id = target_id


class DuplicateSocialLinkException(BusinessRuleViolationException):
    """Социальная ссылка с таким platform уже существует."""

    def __init__(self, platform: str) -> None:
        super().__init__(
            rule="UniqueSocialLinkPlatform",
            message=f"Социальная ссылка для платформы {platform} уже существует",
        )
        self.platform = platform
