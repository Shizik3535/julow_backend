from celery import Celery
from celery.schedules import crontab

from app.core.config.celery_settings import CelerySettings


def create_celery_app(settings: CelerySettings) -> Celery:
    """
    Создаёт и настраивает Celery приложение.

    Используется Redis как брокер и backend для результатов.
    Задачи регистрируются в Bounded Context'ах.

    Аргументы:
        settings: Настройки Celery.
    """
    app = Celery(
        "julow",
        broker=settings.broker_url,
        backend=settings.result_backend,
    )

    app.conf.update(
        task_serializer=settings.task_serializer,
        accept_content=settings.accept_content,
        result_serializer=settings.result_serializer,
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        beat_schedule={
            "check-task-deadlines": {
                "task": "scheduling.check_task_deadlines",
                "schedule": crontab(minute=0),  # каждый час
            },
            "check-overdue-tasks": {
                "task": "scheduling.check_overdue_tasks",
                "schedule": crontab(minute=15),  # каждый час со сдвигом
            },
            "check-project-deadlines": {
                "task": "scheduling.check_project_deadlines",
                "schedule": crontab(minute=30),  # каждый час со сдвигом
            },
            "check-overdue-projects": {
                "task": "scheduling.check_overdue_projects",
                "schedule": crontab(minute=45),  # каждый час со сдвигом
            },
        },
    )

    return app
