from __future__ import annotations

from typing import Any

from app.core.logging import get_logger
from app.shared.application.ports.background_tasks.background_tasks_port import (
    BackgroundTasksPort,
)

logger = get_logger(__name__)

# Имя зарегистрированной Celery-задачи (см. ``main.py``).
SCAN_TASK_NAME = "filestorage.scan_file_for_virus"


class OnFileUploadedScanForVirus:
    """
    Обработчик события ``FileUploaded`` (FileStorage BC).

    Ставит в очередь Celery-таск для асинхронного антивирусного
    сканирования файла. Файл при этом остаётся со статусом ``PENDING``
    до завершения скана.
    """

    def __init__(self, background_tasks: BackgroundTasksPort) -> None:
        self._background_tasks = background_tasks

    async def handle(self, message: dict[str, Any]) -> None:
        event_type = message.get("event_type") or message.get("type")
        if event_type != "FileUploaded":
            return

        payload = message.get("payload") or message
        file_id = payload.get("file_id")
        if not file_id:
            return

        # send_task — Celery-only; для NoOp/asyncio fallback BackgroundTasksPort
        # это будет no-op, тест-режим обойдётся без сканирования.
        send_task = getattr(self._background_tasks, "send_task", None)
        if send_task is None:
            logger.warning(
                "BackgroundTasksPort does not support send_task; scan skipped",
                file_id=file_id,
            )
            return

        send_task(name=SCAN_TASK_NAME, args=(file_id,))
        logger.info(
            "Virus scan task enqueued",
            file_id=file_id,
            task=SCAN_TASK_NAME,
        )
