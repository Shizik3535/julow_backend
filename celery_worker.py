"""
Celery worker entry point.

Запуск:
    celery -A celery_worker.celery_app worker --loglevel=info
"""

from app.core.config.celery_settings import CelerySettings
from app.core.di.providers.background_tasks_provider import create_celery_app
from app.context.filestorage.infrastructure.scheduling.celery_tasks import (
    scan_file_for_virus_task,
)
from app.context.task.infrastructure.scheduling.celery_tasks import (
    check_task_deadlines_task,
    check_overdue_tasks_task,
)
from app.context.project.infrastructure.scheduling.celery_tasks import (
    check_project_deadlines_task,
    check_overdue_projects_task,
)

settings = CelerySettings()
celery_app = create_celery_app(settings)

# Register all tasks
celery_app.task(name="filestorage.scan_file_for_virus")(scan_file_for_virus_task)
celery_app.task(name="scheduling.check_task_deadlines")(check_task_deadlines_task)
celery_app.task(name="scheduling.check_overdue_tasks")(check_overdue_tasks_task)
celery_app.task(name="scheduling.check_project_deadlines")(check_project_deadlines_task)
celery_app.task(name="scheduling.check_overdue_projects")(check_overdue_projects_task)
