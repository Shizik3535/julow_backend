"""Unit-тесты для проектного чата (Chat.create_project_chat и system-операций).

Покрывают регрессию для требования: при наличии в проекте ≥ 2 участников
автоматически создаётся групповой чат, привязанный к проекту. Чат сохраняется
между сессиями приглашений (новые участники добавляются в существующий чат),
а при архивации проекта чат архивируется, но история сохраняется.
"""

from __future__ import annotations

import uuid

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.communication.domain.aggregates.chat import Chat
from app.context.communication.domain.events.chat_events import (
    ChatCreated,
    ChatMemberAdded,
    ChatMemberRemoved,
)
from app.context.communication.domain.value_objects.chat_member_role import (
    ChatMemberRole,
)
from app.context.communication.domain.value_objects.chat_type import ChatType


def _new_id() -> Id:
    return Id(value=uuid.uuid4())


# ═══════════════════════════════════════════════════════════════════════════
# create_project_chat
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCreateProjectChat:
    def test_creates_group_chat_with_project_id(self) -> None:
        project_id = _new_id()
        workspace_id = _new_id()
        owner = _new_id()
        member = _new_id()

        chat = Chat.create_project_chat(
            name="Проект Альфа",
            project_id=project_id,
            workspace_id=workspace_id,
            member_ids=[owner, member],
            owner_id=owner,
        )

        assert chat.chat_type == ChatType.GROUP
        assert chat.project_id == project_id
        assert chat.workspace_id == workspace_id
        assert chat.name == "Проект Альфа"
        assert len(chat.members) == 2

    def test_owner_is_assigned_owner_role(self) -> None:
        owner = _new_id()
        member = _new_id()
        chat = Chat.create_project_chat(
            name="P",
            project_id=_new_id(),
            workspace_id=None,
            member_ids=[owner, member],
            owner_id=owner,
        )

        owner_member = next(m for m in chat.members if m.user_id == owner)
        regular_member = next(m for m in chat.members if m.user_id == member)
        assert owner_member.role == ChatMemberRole.OWNER
        assert regular_member.role == ChatMemberRole.MEMBER

    def test_deduplicates_members(self) -> None:
        """Если owner также передан в member_ids — он не дублируется."""
        owner = _new_id()
        other = _new_id()
        chat = Chat.create_project_chat(
            name="P",
            project_id=_new_id(),
            workspace_id=None,
            member_ids=[owner, other, owner],
            owner_id=owner,
        )
        assert len(chat.members) == 2

    def test_emits_chat_created_event(self) -> None:
        chat = Chat.create_project_chat(
            name="P",
            project_id=_new_id(),
            workspace_id=None,
            member_ids=[_new_id()],
            owner_id=None,
        )
        events = chat.clear_domain_events()
        assert any(isinstance(e, ChatCreated) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# system_add_member / system_remove_member
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestChatSystemOperations:
    def test_system_add_member_adds_new_member(self) -> None:
        owner = _new_id()
        chat = Chat.create_project_chat(
            name="P",
            project_id=_new_id(),
            workspace_id=None,
            member_ids=[owner],
            owner_id=owner,
        )
        chat.clear_domain_events()

        new_member = _new_id()
        chat.system_add_member(new_member)

        assert any(m.user_id == new_member for m in chat.members)
        events = chat.clear_domain_events()
        assert any(isinstance(e, ChatMemberAdded) for e in events)

    def test_system_add_member_is_idempotent(self) -> None:
        owner = _new_id()
        chat = Chat.create_project_chat(
            name="P",
            project_id=_new_id(),
            workspace_id=None,
            member_ids=[owner],
            owner_id=owner,
        )
        chat.clear_domain_events()

        chat.system_add_member(owner)  # уже есть
        assert len(chat.members) == 1
        events = chat.clear_domain_events()
        assert not events

    def test_system_add_member_works_even_when_archived(self) -> None:
        """archive()-чат не должен бросать ChatArchivedException на system_*."""
        owner = _new_id()
        chat = Chat.create_project_chat(
            name="P",
            project_id=_new_id(),
            workspace_id=None,
            member_ids=[owner],
            owner_id=owner,
        )
        chat.archive()
        chat.clear_domain_events()

        new_member = _new_id()
        chat.system_add_member(new_member)  # не должно бросить
        assert any(m.user_id == new_member for m in chat.members)

    def test_system_remove_member_removes(self) -> None:
        owner = _new_id()
        member = _new_id()
        chat = Chat.create_project_chat(
            name="P",
            project_id=_new_id(),
            workspace_id=None,
            member_ids=[owner, member],
            owner_id=owner,
        )
        chat.clear_domain_events()

        chat.system_remove_member(member)

        assert all(m.user_id != member for m in chat.members)
        events = chat.clear_domain_events()
        assert any(isinstance(e, ChatMemberRemoved) for e in events)

    def test_system_remove_member_is_idempotent(self) -> None:
        owner = _new_id()
        chat = Chat.create_project_chat(
            name="P",
            project_id=_new_id(),
            workspace_id=None,
            member_ids=[owner],
            owner_id=owner,
        )
        chat.clear_domain_events()

        chat.system_remove_member(_new_id())  # участника нет
        events = chat.clear_domain_events()
        assert not events

    def test_system_remove_owner_reassigns_owner(self) -> None:
        """Если удаляем owner'а — следующему участнику передаётся роль OWNER."""
        owner = _new_id()
        member = _new_id()
        chat = Chat.create_project_chat(
            name="P",
            project_id=_new_id(),
            workspace_id=None,
            member_ids=[owner, member],
            owner_id=owner,
        )

        chat.system_remove_member(owner)

        remaining = next(m for m in chat.members if m.user_id == member)
        assert remaining.role == ChatMemberRole.OWNER

    def test_system_remove_member_works_when_archived(self) -> None:
        owner = _new_id()
        member = _new_id()
        chat = Chat.create_project_chat(
            name="P",
            project_id=_new_id(),
            workspace_id=None,
            member_ids=[owner, member],
            owner_id=owner,
        )
        chat.archive()
        chat.clear_domain_events()

        chat.system_remove_member(member)
        assert all(m.user_id != member for m in chat.members)


# ═══════════════════════════════════════════════════════════════════════════
# Жизненный цикл archive / restore
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestChatArchiveRestore:
    def test_archive_is_idempotent(self) -> None:
        chat = Chat.create_project_chat(
            name="P",
            project_id=_new_id(),
            workspace_id=None,
            member_ids=[_new_id()],
        )
        chat.archive()
        assert chat.is_archived
        chat.archive()  # повторный вызов не должен сломаться
        assert chat.is_archived

    def test_restore_brings_chat_back(self) -> None:
        chat = Chat.create_project_chat(
            name="P",
            project_id=_new_id(),
            workspace_id=None,
            member_ids=[_new_id()],
        )
        chat.archive()
        chat.restore()
        assert not chat.is_archived
