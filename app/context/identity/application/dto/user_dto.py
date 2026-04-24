from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO


class UserDTO(BaseDTO):
    """
    DTO пользователя (Identity BC).

    Атрибуты:
        id: Идентификатор пользователя.
        email: Email-адрес.
        status: Статус аккаунта.
        role_ids: Список ID ролей.
        is_email_confirmed: Подтверждён ли email.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    id: str
    email: str
    status: str
    role_ids: list[str]
    is_email_confirmed: bool
    created_at: datetime
    updated_at: datetime
