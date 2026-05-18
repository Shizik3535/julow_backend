"""Unit-тесты для обработчика ``OnProjectMemberJoinedSyncChat``.

Покрывают:
- чат не создаётся, если в проекте < 2 участников;
- чат автоматически создаётся, когда участников становится 2;
- последующее присоединение участника не создаёт новый чат, а добавляет
  его в существующий;
- архивированный чат не мутируется при добавлении новых участников
  (этот сценарий не должен встречаться в проде, но handler не должен падать).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Optional

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.communication.application.event_handlers.on_project_member_joined_sync_chat import (
    OnProjectMemberJoinedSyncChat,
)
from app.context.communication.domain.aggregates.chat import Chat
from app.context.communication.domain.value_objects.chat_type import ChatType
from app.context.project.application.dto.project_dto import ProjectDTO


# ─── Test doubles ──────────────────────────────────────────────────────────


class _StubChatRepository:
    def __init__(self) -> None:
        self._by_project: dict[str, Chat] = {}
        self.added: list[Chat] = []
        self.updated: list[Chat] = []

    async def get_by_project_id(self, project_id: Id) -> Chat | None:
        return self._by_project.get(str(project_id))

    async def add(self, chat: Chat) -> Chat:
        self.added.append(chat)
        if chat.project_id is not None:
            self._by_project[str(chat.project_id)] = chat
        return chat

    async def update(self, chat: Chat) -> Chat:
        self.updated.append(chat)
        return chat


class _StubProjectProvider:
    def __init__(self, project: ProjectDTO | None) -> None:
        self._project = project

    async def get_project(self, project_id: str) -> ProjectDTO | None:
        return self._project

    async def project_exists(self, project_id: str) -> bool:
        return self._project is not None

    async def get_projects_by_workspace(self, workspace_id: str) -> list[ProjectDTO]:
        return [self._project] if self._project else []


class _StubMembershipProvider:
    def __init__(self, member_ids: list[str]) -> None:
        self._member_ids = member_ids

    async def is_project_member(self, project_id: str, user_id: str) -> bool:
        return user_id in self._member_ids

    async def get_member(self, project_id: str, user_id: str):
        return None

    async def get_member_role(self, project_id: str, user_id: str):
        return None

    async def get_project_member_ids(self, project_id: str) -> list[str]:
        return list(self._member_ids)


class _CapturingEventBus:
    def __init__(self) -> None:
        self.events: list = []

    async def publish_all(self, events: list) -> None:
        self.events.extend(events)


def _project_dto(project_id: Id, workspace_id: Id, owner_id: Id, name: str = "P") -> ProjectDTO:
    return ProjectDTO(
        id=str(project_id),
        workspace_id=str(workspace_id),
        name=name,
        owner_ids=[str(owner_id)],
    )


# ─── Tests ──────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestOnProjectMemberJoinedSyncChat:
    async def test_does_not_create_chat_for_solo_project(self) -> None:
        project_id = Id(value=uuid.uuid4())
        workspace_id = Id(value=uuid.uuid4())
        owner_id = Id(value=uuid.uuid4())

        repo = _StubChatRepository()
        handler = OnProjectMemberJoinedSyncChat(
            chat_repo=repo,
            project_provider=_StubProjectProvider(
                _project_dto(project_id, workspace_id, owner_id),
            ),
            project_membership_provider=_StubMembershipProvider([str(owner_id)]),
            event_bus=_CapturingEventBus(),
        )

        await handler.handle({
            "event_type": "ProjectMemberJoined",
            "payload": {
                "project_id": str(project_id),
                "user_id": str(owner_id),
                "role_id": "",
            },
        })

        assert repo.added == []
        assert repo.updated == []

    async def test_creates_chat_when_second_member_joins(self) -> None:
        project_id = Id(value=uuid.uuid4())
        workspace_id = Id(value=uuid.uuid4())
        owner_id = Id(value=uuid.uuid4())
        invitee_id = Id(value=uuid.uuid4())

        repo = _StubChatRepository()
        bus = _CapturingEventBus()
        handler = OnProjectMemberJoinedSyncChat(
            chat_repo=repo,
            project_provider=_StubProjectProvider(
                _project_dto(project_id, workspace_id, owner_id, name="Альфа"),
            ),
            project_membership_provider=_StubMembershipProvider(
                [str(owner_id), str(invitee_id)],
            ),
            event_bus=bus,
        )

        await handler.handle({
            "event_type": "ProjectMemberJoined",
            "payload": {
                "project_id": str(project_id),
                "user_id": str(invitee_id),
                "role_id": "",
            },
        })

        assert len(repo.added) == 1
        chat = repo.added[0]
        assert chat.chat_type == ChatType.GROUP
        assert chat.project_id == project_id
        assert chat.workspace_id == workspace_id
        assert chat.name == "Альфа"
        member_ids = {str(m.user_id) for m in chat.members}
        assert member_ids == {str(owner_id), str(invitee_id)}

    async def test_adds_member_to_existing_chat(self) -> None:
        project_id = Id(value=uuid.uuid4())
        workspace_id = Id(value=uuid.uuid4())
        owner_id = Id(value=uuid.uuid4())
        existing_member = Id(value=uuid.uuid4())
        new_member = Id(value=uuid.uuid4())

        repo = _StubChatRepository()
        # preseed: чат уже существует с owner + 1 участник
        pre_chat = Chat.create_project_chat(
            name="Альфа",
            project_id=project_id,
            workspace_id=workspace_id,
            member_ids=[owner_id, existing_member],
            owner_id=owner_id,
        )
        pre_chat.clear_domain_events()
        repo._by_project[str(project_id)] = pre_chat

        handler = OnProjectMemberJoinedSyncChat(
            chat_repo=repo,
            project_provider=_StubProjectProvider(
                _project_dto(project_id, workspace_id, owner_id),
            ),
            project_membership_provider=_StubMembershipProvider(
                [str(owner_id), str(existing_member), str(new_member)],
            ),
            event_bus=_CapturingEventBus(),
        )

        await handler.handle({
            "event_type": "ProjectMemberJoined",
            "payload": {
                "project_id": str(project_id),
                "user_id": str(new_member),
                "role_id": "",
            },
        })

        # Не должно быть нового чата — только update существующего.
        assert repo.added == []
        assert len(repo.updated) == 1
        assert any(m.user_id == new_member for m in pre_chat.members)

    async def test_skips_archived_chat(self) -> None:
        project_id = Id(value=uuid.uuid4())
        workspace_id = Id(value=uuid.uuid4())
        owner_id = Id(value=uuid.uuid4())
        new_member = Id(value=uuid.uuid4())

        repo = _StubChatRepository()
        archived_chat = Chat.create_project_chat(
            name="Альфа",
            project_id=project_id,
            workspace_id=workspace_id,
            member_ids=[owner_id],
            owner_id=owner_id,
        )
        archived_chat.archive()
        archived_chat.clear_domain_events()
        repo._by_project[str(project_id)] = archived_chat

        handler = OnProjectMemberJoinedSyncChat(
            chat_repo=repo,
            project_provider=_StubProjectProvider(
                _project_dto(project_id, workspace_id, owner_id),
            ),
            project_membership_provider=_StubMembershipProvider(
                [str(owner_id), str(new_member)],
            ),
            event_bus=_CapturingEventBus(),
        )

        await handler.handle({
            "event_type": "ProjectMemberJoined",
            "payload": {
                "project_id": str(project_id),
                "user_id": str(new_member),
                "role_id": "",
            },
        })

        assert repo.updated == []
        assert all(m.user_id != new_member for m in archived_chat.members)

    async def test_ignores_unrelated_event_type(self) -> None:
        repo = _StubChatRepository()
        handler = OnProjectMemberJoinedSyncChat(
            chat_repo=repo,
            project_provider=_StubProjectProvider(None),
            project_membership_provider=_StubMembershipProvider([]),
            event_bus=_CapturingEventBus(),
        )

        await handler.handle({
            "event_type": "SomethingElse",
            "payload": {"project_id": str(uuid.uuid4()), "user_id": str(uuid.uuid4())},
        })

        assert repo.added == []
        assert repo.updated == []
