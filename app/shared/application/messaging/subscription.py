from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession


MessageHandlerFn = Callable[[dict[str, Any]], Awaitable[None]]
"""Асинхронный обработчик одного сообщения, пришедшего из брокера."""

SubscriptionHandlerBuilder = Callable[[AsyncSession], MessageHandlerFn]
"""
Фабрика обработчика, получающая per-message сессию БД.

Используется, чтобы каждый consume открывал свежую AsyncSession
с собственной транзакцией и своим набором репозиториев.
"""


@dataclass(frozen=True)
class Subscription:
    """
    Декларативное описание подписки Bounded Context'а на топик брокера.

    Поля:
        topic: Имя входящего топика (например ``"identity.events"``).
        group_id: Идентификатор consumer-группы (обычно ``"<bc>-bc"``).
        build_handler: Фабрика, создающая обработчик сообщения
            с учётом per-message сессии БД (см. ``subscribe_with_uow``).
    """

    topic: str
    group_id: str
    build_handler: SubscriptionHandlerBuilder
