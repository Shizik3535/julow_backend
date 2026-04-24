from __future__ import annotations

from typing import Any, AsyncContextManager, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.shared.application.messaging.subscription import Subscription
from app.shared.application.ports.messaging.message_broker_port import MessageBrokerPort


SessionFactory = Callable[[], AsyncContextManager[AsyncSession]]

logger = get_logger(__name__)


async def subscribe_with_uow(
    broker: MessageBrokerPort,
    session_factory: SessionFactory,
    subscription: Subscription,
) -> None:
    """
    Подписать обработчик на топик с транзакционной обёрткой (Unit of Work).

    Для каждого входящего сообщения:
    1. Открывается новая ``AsyncSession`` из ``session_factory``.
    2. Через ``subscription.build_handler(session)`` создаётся
       обработчик с репозиториями, привязанными к этой сессии.
    3. При успехе — ``commit``; при исключении — ``rollback`` и повторный raise
       (брокер сам решит, ретраить ли сообщение).

    Аргументы:
        broker: Порт брокера сообщений.
        session_factory: Фабрика AsyncSession (context manager).
        subscription: Описание подписки BC.
    """

    async def _handler(topic: str, message: dict[str, Any]) -> None:
        async with session_factory() as session:
            try:
                handler_fn = subscription.build_handler(session)
                await handler_fn(message)
                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception(
                    "Subscription handler failed",
                    topic=subscription.topic,
                    group_id=subscription.group_id,
                )
                raise

    await broker.subscribe(
        topic=subscription.topic,
        group_id=subscription.group_id,
        handler=_handler,
    )
