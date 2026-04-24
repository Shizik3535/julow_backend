from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SessionResponse(BaseModel):
    """
    Ответ с данными сессии пользователя.

    Содержит информацию об активной или завершённой сессии,
    включая устройство и IP-адрес.

    Атрибуты:
        id: UUID сессии.
        user_id: UUID пользователя-владельца.
        device_info: User-Agent устройства.
        ip_address: IP-адрес, с которого создана сессия.
        status: Статус сессии (active, expired, terminated).
        is_remember_me: Был ли включён флаг «Запомнить меня».
        created_at: Дата создания сессии (UTC).
        expires_at: Дата истечения сессии (UTC).
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID сессии", examples=["550e8400-e29b-41d4-a716-446655440000"])
    user_id: str = Field(..., description="UUID пользователя")
    device_info: str = Field(..., description="User-Agent устройства", examples=["Mozilla/5.0 ..."])
    ip_address: str = Field(..., description="IP-адрес клиента", examples=["192.168.1.1"])
    status: str = Field(..., description="Статус сессии", examples=["active"])
    is_remember_me: bool = Field(..., description="Флаг «Запомнить меня»")
    created_at: datetime = Field(..., description="Дата создания сессии (UTC)")
    expires_at: datetime = Field(..., description="Дата истечения сессии (UTC)")
