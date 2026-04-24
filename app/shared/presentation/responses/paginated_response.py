from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, computed_field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Метаданные пагинации."""

    total: int = Field(..., description="Общее количество элементов")
    page: int = Field(..., description="Номер текущей страницы (1-based)")
    page_size: int = Field(..., description="Размер страницы")
    pages: int = Field(..., description="Общее количество страниц")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Ответ с пагинированными данными.

    Поддерживает дженерики: PaginatedResponse[SomeDTO] — Swagger покажет схему SomeDTO.

    Атрибуты:
        success: Всегда True.
        items: Список элементов текущей страницы.
        pagination: Метаданные пагинации.
    """

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    success: bool = True
    items: list[Any] = Field(default_factory=list)
    total: int = Field(..., description="Общее количество элементов")
    page: int = Field(..., description="Номер текущей страницы")
    page_size: int = Field(..., description="Размер страницы")

    @computed_field
    @property
    def pagination(self) -> PaginationMeta:
        """Метаданные пагинации (автовычисляемое поле)."""
        pages = -(-self.total // self.page_size) if self.page_size > 0 else 0
        return PaginationMeta(
            total=self.total,
            page=self.page,
            page_size=self.page_size,
            pages=pages,
        )
