from __future__ import annotations

import re

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException


_EMOJI_PATTERN = re.compile(
    r"^[\U0001F600-\U0001F64F"  # emoticons
    r"\U0001F300-\U0001F5FF"     # symbols & pictographs
    r"\U0001F680-\U0001F6FF"     # transport & map
    r"\U0001F1E0-\U0001F1FF"     # flags
    r"\U00002702-\U000027B0"     # dingbats
    r"\U0000FE00-\U0000FE0F"     # variation selectors
    r"\U0001F900-\U0001F9FF"     # supplemental symbols
    r"\U0001FA00-\U0001FA6F"     # chess symbols
    r"\U0001FA70-\U0001FAFF"     # symbols extended-A
    r"\U00002600-\U000026FF"     # misc symbols
    r"\u200d"                    # zero-width joiner
    r"\ufe0f"                    # variation selector-16
    r"\U0000200B"                # zero-width space
    r"]+$"
)


@dataclass(frozen=True)
class ReactionEmoji(ValueObject):
    """
    Value Object для emoji-реакции.

    Валидирует, что значение является unicode emoji.

    Атрибуты:
        value: Unicode emoji символ.
    """

    value: str = "👍"

    def __post_init__(self) -> None:
        if not self.value or not _EMOJI_PATTERN.match(self.value):
            raise ValidationException(
                field="reaction_emoji",
                message=f"Некорректный emoji: {self.value}",
            )

    def __str__(self) -> str:
        return self.value
