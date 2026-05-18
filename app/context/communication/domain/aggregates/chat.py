from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.color_vo import Color
from app.context.communication.domain.value_objects.chat_type import ChatType
from app.context.communication.domain.value_objects.chat_member_role import ChatMemberRole
from app.context.communication.domain.entities.chat_member import ChatMember
from app.context.communication.domain.entities.thread import Thread
from app.context.communication.domain.events.chat_events import (
    ChatCreated,
    ChatUpdated,
    ChatMemberAdded,
    ChatMemberRemoved,
    ChatMemberRoleChanged,
    ThreadCreated,
    ThreadResolved,
    ThreadReopened,
)
from app.context.communication.domain.exceptions.chat_exceptions import (
    CannotAddMemberToDMException,
    CannotRemoveChatOwnerException,
    CannotRemoveFromDMException,
    ChatArchivedException,
    NotChatMemberException,
    ThreadNotFoundException,
    ThreadAlreadyResolvedException,
)


@dataclass
class Chat(AggregateRoot):
    """
    Корень агрегата чата (Communication BC).

    Поддерживает DM, групповые чаты, каналы и каналы объявлений.

    Атрибуты:
        chat_type: Тип чата.
        name: Название (обязательно для GROUP/CHANNEL/ANNOUNCEMENT).
        description: Описание.
        icon: Название иконки.
        color: Цвет (из shared kernel).
        workspace_id: Opaque ID workspace (для CHANNEL/ANNOUNCEMENT).
        project_id: Opaque ID проекта (для системных проектных чатов,
            создаваемых обработчиками ``project.events``).
        members: Список участников.
        threads: Список тредов.
        last_message_at: Время последнего сообщения.
        is_archived: Архивирован ли чат.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    chat_type: ChatType = ChatType.DM
    name: str | None = None
    description: str | None = None
    icon: str | None = None
    color: Color | None = None
    workspace_id: Id | None = None
    project_id: Id | None = None
    members: list[ChatMember] = field(default_factory=list)
    threads: list[Thread] = field(default_factory=list)
    last_message_at: datetime | None = None
    is_archived: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    # --- Фабричные методы ---

    @classmethod
    def create_dm(cls, user_a: Id, user_b: Id) -> Chat:
        """Создаёт личный диалог (строго 2 участника)."""
        chat = cls(chat_type=ChatType.DM)
        chat.members = [
            ChatMember(user_id=user_a, role=ChatMemberRole.MEMBER),
            ChatMember(user_id=user_b, role=ChatMemberRole.MEMBER),
        ]
        chat._register_event(ChatCreated(chat_id=str(chat.id), chat_type=ChatType.DM))
        return chat

    @classmethod
    def create_group(cls, name: str, creator_id: Id) -> Chat:
        """Создаёт групповой чат."""
        chat = cls(chat_type=ChatType.GROUP, name=name)
        chat.members = [
            ChatMember(user_id=creator_id, role=ChatMemberRole.OWNER),
        ]
        chat._register_event(ChatCreated(chat_id=str(chat.id), chat_type=ChatType.GROUP))
        return chat

    @classmethod
    def create_channel(cls, name: str, workspace_id: Id, creator_id: Id) -> Chat:
        """Создаёт публичный канал."""
        chat = cls(chat_type=ChatType.CHANNEL, name=name, workspace_id=workspace_id)
        chat.members = [
            ChatMember(user_id=creator_id, role=ChatMemberRole.OWNER),
        ]
        chat._register_event(ChatCreated(chat_id=str(chat.id), chat_type=ChatType.CHANNEL))
        return chat

    @classmethod
    def create_announcement(cls, name: str, workspace_id: Id, creator_id: Id) -> Chat:
        """Создаёт канал объявлений."""
        chat = cls(chat_type=ChatType.ANNOUNCEMENT, name=name, workspace_id=workspace_id)
        chat.members = [
            ChatMember(user_id=creator_id, role=ChatMemberRole.OWNER),
        ]
        chat._register_event(ChatCreated(chat_id=str(chat.id), chat_type=ChatType.ANNOUNCEMENT))
        return chat

    @classmethod
    def create_project_chat(
        cls,
        name: str,
        project_id: Id,
        workspace_id: Id | None,
        member_ids: list[Id],
        owner_id: Id | None = None,
    ) -> Chat:
        """
        Создаёт системный групповой чат для проекта.

        Чат автоматически синхронизируется с участниками проекта через
        обработчики событий ``project.events`` и не имеет владельца-человека.
        """
        chat = cls(
            chat_type=ChatType.GROUP,
            name=name,
            workspace_id=workspace_id,
            project_id=project_id,
        )
        owner = owner_id if owner_id is not None else (member_ids[0] if member_ids else None)
        members: list[ChatMember] = []
        seen: set[str] = set()
        if owner is not None:
            owner_key = str(owner)
            members.append(ChatMember(user_id=owner, role=ChatMemberRole.OWNER))
            seen.add(owner_key)
        for user_id in member_ids:
            key = str(user_id)
            if key in seen:
                continue
            members.append(ChatMember(user_id=user_id, role=ChatMemberRole.MEMBER))
            seen.add(key)
        chat.members = members
        chat._register_event(ChatCreated(chat_id=str(chat.id), chat_type=ChatType.GROUP))
        return chat

    # --- Инварианты ---

    def _assert_not_archived(self) -> None:
        if self.is_archived:
            raise ChatArchivedException()

    def _find_member(self, user_id: Id) -> ChatMember | None:
        return next((m for m in self.members if m.user_id == user_id), None)

    def _get_member(self, user_id: Id) -> ChatMember:
        member = self._find_member(user_id)
        if member is None:
            raise NotChatMemberException()
        return member

    def is_member(self, user_id: Id) -> bool:
        return self._find_member(user_id) is not None

    # --- Информация ---

    def update_info(
        self,
        name: str | None = None,
        description: str | None = None,
        icon: str | None = None,
        color: Color | None = None,
    ) -> None:
        self._assert_not_archived()
        changed: list[str] = []
        if name is not None and self.name != name:
            self.name = name
            changed.append("name")
        if description is not None and self.description != description:
            self.description = description
            changed.append("description")
        if icon is not None and self.icon != icon:
            self.icon = icon
            changed.append("icon")
        if color is not None and self.color != color:
            self.color = color
            changed.append("color")
        if changed:
            self.updated_at = datetime.now(tz=timezone.utc)
            self._register_event(ChatUpdated(chat_id=str(self.id), changed_fields=changed))

    # --- Участники ---

    def add_member(self, user_id: Id) -> None:
        self._assert_not_archived()
        if self.chat_type == ChatType.DM:
            raise CannotAddMemberToDMException()
        if self._find_member(user_id) is not None:
            return
        member = ChatMember(user_id=user_id, role=ChatMemberRole.MEMBER)
        self.members.append(member)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            ChatMemberAdded(chat_id=str(self.id), user_id=str(user_id))
        )

    def system_add_member(self, user_id: Id) -> None:
        """
        Идемпотентно добавляет участника от имени системы (без проверки архива).

        Используется обработчиками событий других BC для синхронизации
        участников проектных чатов.
        """
        if self.chat_type == ChatType.DM:
            return
        if self._find_member(user_id) is not None:
            return
        member = ChatMember(user_id=user_id, role=ChatMemberRole.MEMBER)
        self.members.append(member)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            ChatMemberAdded(chat_id=str(self.id), user_id=str(user_id))
        )

    def remove_member(self, user_id: Id) -> None:
        self._assert_not_archived()
        if self.chat_type == ChatType.DM:
            raise CannotRemoveFromDMException()
        member = self._find_member(user_id)
        if member is None:
            return
        if member.role == ChatMemberRole.OWNER:
            raise CannotRemoveChatOwnerException()
        self.members.remove(member)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            ChatMemberRemoved(chat_id=str(self.id), user_id=str(user_id))
        )

    def system_remove_member(self, user_id: Id) -> None:
        """
        Идемпотентно удаляет участника от имени системы.

        Если участник — единственный владелец, у него меняется только запись
        о членстве, но владельца назначаем следующему участнику. Этим
        обеспечивается, что у архивированного чата всегда остаётся хотя бы
        формальный владелец в истории.
        """
        if self.chat_type == ChatType.DM:
            return
        member = self._find_member(user_id)
        if member is None:
            return
        was_owner = member.role == ChatMemberRole.OWNER
        self.members.remove(member)
        if was_owner:
            next_owner = next(iter(self.members), None)
            if next_owner is not None:
                next_owner.role = ChatMemberRole.OWNER
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            ChatMemberRemoved(chat_id=str(self.id), user_id=str(user_id))
        )

    def change_member_role(self, user_id: Id, new_role: ChatMemberRole) -> None:
        self._assert_not_archived()
        member = self._get_member(user_id)
        member.role = new_role
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            ChatMemberRoleChanged(chat_id=str(self.id), user_id=str(user_id), new_role=new_role)
        )

    def mark_as_read(self, user_id: Id, read_at: datetime) -> None:
        member = self._get_member(user_id)
        member.last_read_at = read_at
        self.updated_at = datetime.now(tz=timezone.utc)

    # --- Треды ---

    def create_thread(self, parent_message_id: Id, title: str | None = None) -> Thread:
        self._assert_not_archived()
        thread = Thread(parent_message_id=parent_message_id, title=title)
        self.threads.append(thread)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            ThreadCreated(
                thread_id=str(thread.id),
                chat_id=str(self.id),
                parent_message_id=str(parent_message_id),
            )
        )
        return thread

    def resolve_thread(self, thread_id: Id) -> None:
        thread = next((t for t in self.threads if t.id == thread_id), None)
        if thread is None:
            raise ThreadNotFoundException(id=thread_id)
        if thread.is_resolved:
            raise ThreadAlreadyResolvedException()
        thread.is_resolved = True
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(ThreadResolved(thread_id=str(thread_id)))

    def reopen_thread(self, thread_id: Id) -> None:
        thread = next((t for t in self.threads if t.id == thread_id), None)
        if thread is None:
            raise ThreadNotFoundException(id=thread_id)
        thread.is_resolved = False
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(ThreadReopened(thread_id=str(thread_id)))

    # --- Жизненный цикл ---

    def archive(self) -> None:
        if self.is_archived:
            return
        self.is_archived = True
        self.updated_at = datetime.now(tz=timezone.utc)

    def restore(self) -> None:
        if not self.is_archived:
            return
        self.is_archived = False
        self.updated_at = datetime.now(tz=timezone.utc)
