from app.context.filestorage.infrastructure.scheduling.celery_tasks import (
    scan_file_for_virus_task,
)

__all__ = ["scan_file_for_virus_task"]
