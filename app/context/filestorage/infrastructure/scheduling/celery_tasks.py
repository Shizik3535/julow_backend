from __future__ import annotations

"""
Celery-обёртки для фоновых задач FileStorage BC.

Задачи регистрируются в ``main.py`` через ``celery_adapter.register_task``.
Каждая обёртка создаёт собственный async event loop и DI-контекст.
"""

import asyncio
import logging

logger = logging.getLogger(__name__)


def scan_file_for_virus_task(file_id: str) -> None:
    """
    Celery-обёртка для антивирусного сканирования.

    Вызывается асинхронно после загрузки файла (``FileUploaded``).
    Создаёт свой DI-контейнер и сессию.
    """
    from app.context.filestorage.application.services.scan_file_service import (
        ScanFileService,
    )

    async def _run() -> None:
        from app.core.di.container import Container

        container = Container()
        session_factory = container.db_session_factory()

        broker = container.message_broker_port()
        await broker.start()

        try:
            async with session_factory() as session:
                try:
                    file_repo = container.file_repo(session=session)
                    file_storage = container.file_storage_port()
                    virus_scanner = container.virus_scanner_port()
                    event_bus = container.filestorage_event_bus()

                    service = ScanFileService(
                        file_repo=file_repo,
                        file_storage=file_storage,
                        virus_scanner=virus_scanner,
                        event_bus=event_bus,
                    )
                    await service.scan(file_id=file_id)
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise
        finally:
            await broker.stop()

    asyncio.run(_run())
