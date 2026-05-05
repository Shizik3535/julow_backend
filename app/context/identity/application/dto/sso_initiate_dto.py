from __future__ import annotations

from app.shared.application.base_dto import BaseDTO


class SSOInitiateDTO(BaseDTO):
    """
    DTO результата инициации SSO-логина.

    Атрибуты:
        redirect_url: URL для редиректа на IdP.
        state: Опциональный state-параметр для CSRF-защиты.
    """

    redirect_url: str
    state: str | None = None
