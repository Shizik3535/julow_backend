from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.context.profile.domain.value_objects.hotkey_action import HotkeyAction
from app.context.profile.domain.exceptions.profile_exceptions import InvalidHotkeyException


@dataclass(frozen=True)
class HotkeyConfig(ValueObject):
    """
    Конфигурация горячей клавиши.

    Атрибуты:
        action: Действие, привязанное к комбинации.
        key_combination: Строковое представление комбинации клавиш (например "Ctrl+K").
        is_enabled: Включена ли горячая клавиша.
    """

    action: HotkeyAction = HotkeyAction.QUICK_ACTION
    key_combination: str = ""
    is_enabled: bool = True

    def __post_init__(self) -> None:
        if not self.key_combination.strip():
            raise InvalidHotkeyException(detail="комбинация клавиш не может быть пустой")
