from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.ip_address_vo import IpAddress
from app.context.identity.domain.value_objects.login_status import LoginStatus


@dataclass
class LoginAttempt(BaseEntity):
    """
    Сущность записи попытки входа.

    Принадлежит агрегату UserAuth. Фиксирует каждую попытку
    входа для аудита и анализа безопасности.

    Атрибуты:
        id: Уникальный идентификатор записи.
        ip: IP-адрес попытки входа.
        user_agent: User-Agent заголовок запроса.
        attempted_at: Время попытки входа.
        was_successful: Была ли попытка успешной.
        login_status: Статус попытки входа.
    """

    ip: IpAddress = field(default_factory=lambda: IpAddress("127.0.0.1"))
    user_agent: str = ""
    attempted_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    was_successful: bool = False
    login_status: LoginStatus = LoginStatus.FAILED

    def __post_init__(self) -> None:
        self.was_successful = self.login_status == LoginStatus.SUCCESS
