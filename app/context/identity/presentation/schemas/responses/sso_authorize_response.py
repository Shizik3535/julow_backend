from __future__ import annotations

from pydantic import BaseModel, Field


class SSOAuthorizeResponse(BaseModel):
    """
    Response-схема инициации SSO-логина.

    Атрибуты:
        redirect_url: URL для редиректа на IdP.
    """

    redirect_url: str = Field(..., description="URL для редиректа на SSO-провайдер")
