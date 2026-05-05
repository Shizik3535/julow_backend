from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class LoginSSOCallbackRequest(BaseModel):
    """
    Request-схема callback от SSO IdP.

    Атрибуты:
        email_domain: Домен email (для определения SSO-конфигурации).
        response_data: Данные ответа от IdP (SAMLResponse, code и т.д.).
    """

    email_domain: str = Field(..., description="Домен email для определения SSO-конфигурации")
    response_data: dict[str, Any] = Field(..., description="Данные ответа от IdP")
