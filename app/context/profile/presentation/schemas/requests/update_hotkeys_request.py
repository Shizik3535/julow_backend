from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class HotkeyInput(BaseModel):
    """
    Входные данные для одной горячей клавиши.

    Атрибуты:
        action: Действие (CREATE_TASK, SEARCH и т.д.).
        key_combination: Комбинация клавиш (Ctrl+K).
        is_enabled: Включена ли горячая клавиша.
    """

    action: str = Field(
        ...,
        description="Действие горячей клавиши",
        examples=["CREATE_TASK", "SEARCH"],
    )
    key_combination: str = Field(
        ...,
        max_length=30,
        description="Комбинация клавиш",
        examples=["Ctrl+K"],
    )
    is_enabled: bool = Field(
        default=True,
        description="Включена ли горячая клавиша",
    )


class UpdateHotkeysRequest(BaseModel):
    """
    Тело запроса обновления конфигурации горячих клавиш.

    Атрибуты:
        hotkeys: Список конфигураций горячих клавиш.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "hotkeys": [
                    {"action": "SEARCH", "key_combination": "Ctrl+K", "is_enabled": True},
                    {"action": "CREATE_TASK", "key_combination": "Ctrl+N", "is_enabled": True},
                ],
            },
        },
    )

    hotkeys: list[HotkeyInput] = Field(
        ...,
        description="Список конфигураций горячих клавиш",
    )
