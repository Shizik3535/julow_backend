"""
Messaging-конфигурация FileStorage BC.

BC описывает:
- в какой топик публикует свои доменные события (`filestorage.events`);
- на какие топики других BC он подписан.

По спецификации (docs/events/filestorage-events.md) FileStorage BC
не подписывается на события других BC. Однако application-слой
может опционально слушать project.events для автоматического создания
папки проекта и organization.events / workspace.events для создания
хранилища при создании org/workspace. Эти подписки реализованы как
опциональные event_handlers и регистрируются здесь.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.application.messaging.broker_domain_event_bus import (
    BrokerDomainEventBus,
)
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.messaging.subscription import MessageHandlerFn, Subscription
from app.shared.application.ports.messaging.message_broker_port import (
    MessageBrokerPort,
)

if TYPE_CHECKING:
    from app.core.di.container import Container


# --- Публикация ---

FILESTORAGE_EVENTS_TOPIC = "filestorage.events"

PROJECT_EVENTS_TOPIC = "project.events"
WORKSPACE_EVENTS_TOPIC = "workspace.events"


def build_filestorage_event_bus(broker: MessageBrokerPort) -> DomainEventBus:
    """Создать DomainEventBus FileStorage BC."""
    return BrokerDomainEventBus(broker=broker, topic=FILESTORAGE_EVENTS_TOPIC)


# --- Подписки ---


def filestorage_subscriptions(container: "Container") -> list[Subscription]:
    """
    Подписки FileStorage BC на топики.

    - Project BC → ProjectCreated: автосоздание папки проекта (FolderType.PROJECT).
    - Workspace BC → WorkspaceCreated: автосоздание хранилища workspace.
    - FileStorage BC (self) → FileUploaded: запуск антивирусного сканирования.
    """
    from app.context.filestorage.application.event_handlers.on_file_uploaded_scan_for_virus import (
        OnFileUploadedScanForVirus,
    )
    from app.context.filestorage.application.event_handlers.on_project_created_create_folder import (
        OnProjectCreatedCreateFolder,
    )
    from app.context.filestorage.application.event_handlers.on_workspace_created_create_storage import (
        OnWorkspaceCreatedCreateStorage,
    )

    def _build_on_project_created(session: AsyncSession) -> MessageHandlerFn:
        folder_repo = container.folder_repo(session=session)
        handler = OnProjectCreatedCreateFolder(folder_repo=folder_repo)

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_workspace_created(session: AsyncSession) -> MessageHandlerFn:
        storage_repo = container.storage_repo(session=session)
        handler = OnWorkspaceCreatedCreateStorage(storage_repo=storage_repo)

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    def _build_on_file_uploaded(session: AsyncSession) -> MessageHandlerFn:
        # Сессия не используется — обработчик ставит таск в Celery,
        # сама проверка идёт в отдельном async-контексте Celery-воркера.
        background_tasks = container.background_tasks_port()
        handler = OnFileUploadedScanForVirus(background_tasks=background_tasks)

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    return [
        Subscription(
            topic=PROJECT_EVENTS_TOPIC,
            group_id="filestorage-bc--project-created",
            build_handler=_build_on_project_created,
        ),
        Subscription(
            topic=WORKSPACE_EVENTS_TOPIC,
            group_id="filestorage-bc--workspace-created",
            build_handler=_build_on_workspace_created,
        ),
        Subscription(
            topic=FILESTORAGE_EVENTS_TOPIC,
            group_id="filestorage-bc--scan-uploaded",
            build_handler=_build_on_file_uploaded,
        ),
    ]
