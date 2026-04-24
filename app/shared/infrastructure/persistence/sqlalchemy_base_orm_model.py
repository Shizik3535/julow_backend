from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseORMModel(DeclarativeBase):
    """
    Базовая ORM-модель SQLAlchemy.

    Предоставляет общие колонки для всех моделей:
    - id: UUID первичный ключ
    - created_at: Время создания (автоматически)
    - updated_at: Время обновления (автоматически)

    Все ORM-модели в проекте наследуются от этого класса.
    Модели находятся в infrastructure-слое и НЕ являются
    доменными объектами. Маппинг Domain ↔ ORM выполняется
    через Data Mapper (base_mapper.py).
    """

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(tz=timezone.utc),
    )
