from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateNavigationRequest(BaseModel):
    """
    Тело запроса обновления настроек навигации.

    Атрибуты:
        start_page: Идентификатор стартовой страницы.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_page": "dashboard",
            },
        },
    )

    start_page: str = Field(
        default="dashboard",
        max_length=50,
        description="Идентификатор стартовой страницы (dashboard, my_tasks, inbox, ...)",
        examples=["dashboard", "my_tasks"],
    )
