"""Unit-тесты обработчиков жизненного цикла проектного чата.

Покрывают:
- ``OnProjectArchivedArchiveChat`` — архивация чата при архивации проекта;
- ``OnProjectDeletionRequestedArchiveChat`` — архивация при удалении проекта;
- ``OnProjectRestoredRestoreChat`` — разархивация при восстановлении или
  реактивации проекта;
- ``OnProjectMemberRemovedSyncChat`` — удаление участника из чата.
"""

from __future__ import annotations

import uuid

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.communication.application.event_handlers.on_project_archived_archive_chat import (
    OnProjectArchivedArchiveChat,
)
from app.context.communication.application.event_handlers.on_project_deletion_requested_archive_chat import (
    OnProjectDeletionRequestedArchiveChat,
)
from app.context.communication.application.event_handlers.on_project_member_removed_sync_chat import (
    OnProjectMemberRemovedSyncChat,
)
from app.context.communication.application.event_handlers.on_project_restored_restore_chat import (
    OnProjectRestoredRestoreChat,
)
from app.context.communication.domain.aggregates.chat import Chat


class _StubChatRepository:
    def __init__(self, chat: Chat | None = None) -> None:
        self._chat = chat
        self.updated: list[Chat] = []

    async def get_by_project_id(self, project_id: Id) -> Chat | None:
        if self._chat is None:
            return None
        if self._chat.project_id == project_id:
            return self._chat
        return None

    async def update(self, chat: Chat) -> Chat:
        self.updated.append(chat)
        return chat


class _CapturingEventBus:
    def __init__(self) -> None:
        self.events: list = []

    async def publish_all(self, events: list) -> None:
        self.events.extend(events)


def _make_chat(project_id: Id, archived: bool = False) -> Chat:
    chat = Chat.create_project_chat(
        name="P",
        project_id=project_id,
        workspace_id=Id(value=uuid.uuid4()),
        member_ids=[Id(value=uuid.uuid4()), Id(value=uuid.uuid4())],
    )
    chat.clear_domain_events()
    if archived:
        chat.archive()
    return chat


# ─── ProjectArchived ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestOnProjectArchivedArchiveChat:
    async def test_archives_active_chat(self) -> None:
        project_id = Id(value=uuid.uuid4())
        chat = _make_chat(project_id, archived=False)
        repo = _StubChatRepository(chat)

        handler = OnProjectArchivedArchiveChat(
            chat_repo=repo, event_bus=_CapturingEventBus(),
        )
        await handler.handle({
            "event_type": "ProjectArchived",
            "payload": {"project_id": str(project_id)},
        })

        assert chat.is_archived
        assert repo.updated == [chat]

    async def test_skips_when_already_archived(self) -> None:
        project_id = Id(value=uuid.uuid4())
        chat = _make_chat(project_id, archived=True)
        repo = _StubChatRepository(chat)

        handler = OnProjectArchivedArchiveChat(
            chat_repo=repo, event_bus=_CapturingEventBus(),
        )
        await handler.handle({
            "event_type": "ProjectArchived",
            "payload": {"project_id": str(project_id)},
        })

        assert repo.updated == []

    async def test_no_chat_no_op(self) -> None:
        repo = _StubChatRepository(None)
        handler = OnProjectArchivedArchiveChat(
            chat_repo=repo, event_bus=_CapturingEventBus(),
        )
        await handler.handle({
            "event_type": "ProjectArchived",
            "payload": {"project_id": str(uuid.uuid4())},
        })
        assert repo.updated == []


# ─── ProjectDeletionRequested ──────────────────────────────────────────────


@pytest.mark.unit
class TestOnProjectDeletionRequestedArchiveChat:
    async def test_archives_chat_on_deletion(self) -> None:
        project_id = Id(value=uuid.uuid4())
        chat = _make_chat(project_id, archived=False)
        repo = _StubChatRepository(chat)

        handler = OnProjectDeletionRequestedArchiveChat(
            chat_repo=repo, event_bus=_CapturingEventBus(),
        )
        await handler.handle({
            "event_type": "ProjectDeletionRequested",
            "payload": {"project_id": str(project_id)},
        })

        assert chat.is_archived
        assert repo.updated == [chat]


# ─── ProjectRestored / ProjectReactivated ───────────────────────────────────


@pytest.mark.unit
class TestOnProjectRestoredRestoreChat:
    @pytest.mark.parametrize("event_type", ["ProjectRestored", "ProjectReactivated"])
    async def test_restores_archived_chat(self, event_type: str) -> None:
        project_id = Id(value=uuid.uuid4())
        chat = _make_chat(project_id, archived=True)
        repo = _StubChatRepository(chat)

        handler = OnProjectRestoredRestoreChat(
            chat_repo=repo, event_bus=_CapturingEventBus(),
        )
        await handler.handle({
            "event_type": event_type,
            "payload": {"project_id": str(project_id)},
        })

        assert not chat.is_archived
        assert repo.updated == [chat]

    async def test_skips_unrelated_event(self) -> None:
        project_id = Id(value=uuid.uuid4())
        chat = _make_chat(project_id, archived=True)
        repo = _StubChatRepository(chat)

        handler = OnProjectRestoredRestoreChat(
            chat_repo=repo, event_bus=_CapturingEventBus(),
        )
        await handler.handle({
            "event_type": "SomethingElse",
            "payload": {"project_id": str(project_id)},
        })

        assert chat.is_archived
        assert repo.updated == []


# ─── ProjectMemberRemoved ──────────────────────────────────────────────────


@pytest.mark.unit
class TestOnProjectMemberRemovedSyncChat:
    async def test_removes_member_from_chat(self) -> None:
        project_id = Id(value=uuid.uuid4())
        owner = Id(value=uuid.uuid4())
        member = Id(value=uuid.uuid4())
        chat = Chat.create_project_chat(
            name="P",
            project_id=project_id,
            workspace_id=None,
            member_ids=[owner, member],
            owner_id=owner,
        )
        chat.clear_domain_events()
        repo = _StubChatRepository(chat)

        handler = OnProjectMemberRemovedSyncChat(
            chat_repo=repo, event_bus=_CapturingEventBus(),
        )
        await handler.handle({
            "event_type": "ProjectMemberRemoved",
            "payload": {"project_id": str(project_id), "user_id": str(member)},
        })

        assert all(m.user_id != member for m in chat.members)
        assert repo.updated == [chat]

    async def test_works_when_chat_archived(self) -> None:
        project_id = Id(value=uuid.uuid4())
        owner = Id(value=uuid.uuid4())
        member = Id(value=uuid.uuid4())
        chat = Chat.create_project_chat(
            name="P",
            project_id=project_id,
            workspace_id=None,
            member_ids=[owner, member],
            owner_id=owner,
        )
        chat.archive()
        chat.clear_domain_events()
        repo = _StubChatRepository(chat)

        handler = OnProjectMemberRemovedSyncChat(
            chat_repo=repo, event_bus=_CapturingEventBus(),
        )
        await handler.handle({
            "event_type": "ProjectMemberRemoved",
            "payload": {"project_id": str(project_id), "user_id": str(member)},
        })

        assert all(m.user_id != member for m in chat.members)
        assert repo.updated == [chat]

    async def test_no_chat_no_op(self) -> None:
        repo = _StubChatRepository(None)
        handler = OnProjectMemberRemovedSyncChat(
            chat_repo=repo, event_bus=_CapturingEventBus(),
        )
        await handler.handle({
            "event_type": "ProjectMemberRemoved",
            "payload": {
                "project_id": str(uuid.uuid4()),
                "user_id": str(uuid.uuid4()),
            },
        })
        assert repo.updated == []
