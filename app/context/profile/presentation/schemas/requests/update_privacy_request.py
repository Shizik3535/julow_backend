from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdatePrivacyRequest(BaseModel):
    """
    Тело запроса обновления настроек приватности.

    Атрибуты:
        profile_visibility: Видимость профиля (public, organization_only, private).
        online_status_visibility: Видимость онлайн-статуса (everyone, contacts_only, nobody).
        activity_tracking_consent: Согласие на отслеживание активности (granted, denied).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "profile_visibility": "organization_only",
                "online_status_visibility": "everyone",
                "activity_tracking_consent": "granted",
            },
        },
    )

    profile_visibility: str = Field(
        default="organization_only",
        description="Видимость профиля (public, organization_only, private)",
        examples=["organization_only"],
    )
    online_status_visibility: str = Field(
        default="everyone",
        description="Видимость онлайн-статуса (everyone, contacts_only, nobody)",
        examples=["everyone"],
    )
    activity_tracking_consent: str = Field(
        default="granted",
        description="Согласие на отслеживание активности (granted, denied)",
        examples=["granted"],
    )
