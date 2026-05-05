from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class LoginSSORequest(BaseModel):
    """
    Request-схема инициации SSO-логина.

    Атрибуты:
        email: Email пользователя (по домену определяется SSO-провайдер).
    """

    email: EmailStr = Field(..., description="Email пользователя для определения SSO-конфигурации")
