from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SidebarSectionInput(BaseModel):
    """
    Входные данные для одной секции sidebar.

    Атрибуты:
        section_id: Идентификатор секции.
        is_collapsed: Свернута ли секция.
        item_ids: Список ID элементов внутри секции.
        order: Порядок секции в sidebar.
    """

    section_id: str = Field(
        ...,
        description="Идентификатор секции",
        examples=["favorites"],
    )
    is_collapsed: bool = Field(
        default=False,
        description="Свернута ли секция",
    )
    item_ids: list[str] = Field(
        default_factory=list,
        description="Список ID элементов внутри секции",
    )
    order: int = Field(
        default=0,
        ge=0,
        description="Порядок секции в sidebar",
    )


class UpdateSidebarRequest(BaseModel):
    """
    Тело запроса обновления конфигурации sidebar.

    Атрибуты:
        sections: Список секций sidebar.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sections": [
                    {
                        "section_id": "favorites",
                        "is_collapsed": False,
                        "item_ids": ["item-1", "item-2"],
                        "order": 0,
                    },
                ],
            },
        },
    )

    sections: list[SidebarSectionInput] = Field(
        ...,
        description="Список секций sidebar",
    )
