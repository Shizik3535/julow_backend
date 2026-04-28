from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RegisterDeviceTokenRequest(BaseModel):
    """
    Тело запроса регистрации push-токена устройства.

    Атрибуты:
        token: Push-токен устройства.
        platform: Платформа (ios/android/web).
        device_name: Название устройства.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "fCMxK3R2v8:APA91bH...",
                "platform": "android",
                "device_name": "Samsung Galaxy S24",
            },
        },
    )

    token: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Push-токен устройства",
        examples=["fCMxK3R2v8:APA91bH..."],
    )
    platform: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Платформа (ios/android/web)",
        examples=["android"],
    )
    device_name: str = Field(
        default="",
        max_length=255,
        description="Название устройства",
        examples=["Samsung Galaxy S24"],
    )
