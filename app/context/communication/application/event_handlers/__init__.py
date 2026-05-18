"""Обработчики кросс-BC событий Communication BC.

Сейчас Communication BC реагирует на события Project BC, чтобы автоматически
поддерживать жизненный цикл проектных чатов:

* участник вступил в проект → синхронизация состава чата (создание чата,
  если в проекте оказалось ≥ 2 участников);
* участник удалён из проекта → удаление из чата;
* проект архивирован / запрошено удаление → архивация чата (история
  переписки сохраняется);
* проект восстановлен / реактивирован → разархивация чата.
"""
from __future__ import annotations

from app.context.communication.application.event_handlers.on_project_archived_archive_chat import (
    OnProjectArchivedArchiveChat,
)
from app.context.communication.application.event_handlers.on_project_deletion_requested_archive_chat import (
    OnProjectDeletionRequestedArchiveChat,
)
from app.context.communication.application.event_handlers.on_project_member_joined_sync_chat import (
    OnProjectMemberJoinedSyncChat,
)
from app.context.communication.application.event_handlers.on_project_member_removed_sync_chat import (
    OnProjectMemberRemovedSyncChat,
)
from app.context.communication.application.event_handlers.on_project_restored_restore_chat import (
    OnProjectRestoredRestoreChat,
)

__all__ = [
    "OnProjectArchivedArchiveChat",
    "OnProjectDeletionRequestedArchiveChat",
    "OnProjectMemberJoinedSyncChat",
    "OnProjectMemberRemovedSyncChat",
    "OnProjectRestoredRestoreChat",
]
