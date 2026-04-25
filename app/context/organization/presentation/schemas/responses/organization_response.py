from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class OrganizationResponse(BaseModel):
    """
    Ответ с данными организации.

    Атрибуты:
        id: UUID организации.
        name: Название организации.
        status: Статус организации.
        owner_ids: Список UUID владельцев.
        personalization: Настройки персонализации.
        security_policy: Политика безопасности.
        membership_policy: Политика членства.
        created_at: Дата создания (UTC).
        updated_at: Дата последнего обновления (UTC).
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="UUID организации",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    name: str = Field(
        ...,
        description="Название организации",
        examples=["Acme Corp"],
    )
    status: str = Field(
        ...,
        description="Статус организации",
        examples=["ACTIVE"],
    )
    owner_ids: list[str] = Field(
        default_factory=list,
        description="Список UUID владельцев",
        examples=[["550e8400-e29b-41d4-a716-446655440000"]],
    )
    personalization: dict[str, Any] = Field(
        default_factory=dict,
        description="Настройки персонализации",
    )
    security_policy: dict[str, Any] = Field(
        default_factory=dict,
        description="Политика безопасности",
    )
    membership_policy: dict[str, Any] = Field(
        default_factory=dict,
        description="Политика членства",
    )
    created_at: datetime = Field(..., description="Дата создания (UTC)")
    updated_at: datetime = Field(..., description="Дата последнего обновления (UTC)")
