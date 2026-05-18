from __future__ import annotations

from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.communication.domain.aggregates.chat import Chat
from app.context.communication.domain.entities.chat_member import ChatMember
from app.context.communication.domain.entities.thread import Thread
from app.context.communication.domain.value_objects.chat_member_role import (
    ChatMemberRole,
)
from app.context.communication.domain.value_objects.chat_type import ChatType
from app.context.communication.infrastructure.persistence.orm_models.chat_orm import (
    ChatMemberORM,
    ChatORM,
    ThreadORM,
)


class ChatMapper(BaseMapper[Chat, ChatORM]):
    """Data Mapper: Chat ↔ ChatORM."""

    def to_domain(self, orm_model: ChatORM) -> Chat:
        members = [
            ChatMember(
                id=self._map_id(m.id),
                user_id=self._map_id(m.user_id),
                role=ChatMemberRole(m.role),
                joined_at=m.joined_at,
                last_read_at=m.last_read_at,
            )
            for m in (orm_model.members or [])
        ]
        threads = [
            Thread(
                id=self._map_id(t.id),
                parent_message_id=self._map_id(t.parent_message_id),
                title=t.title,
                is_resolved=t.is_resolved,
                created_at=t.thread_created_at,
            )
            for t in (orm_model.threads or [])
        ]

        return Chat(
            id=self._map_id(orm_model.id),
            chat_type=ChatType(orm_model.chat_type),
            name=orm_model.name,
            description=orm_model.description,
            icon=orm_model.icon,
            color=Color(value=orm_model.color) if orm_model.color else None,
            workspace_id=(
                self._map_id(orm_model.workspace_id)
                if orm_model.workspace_id
                else None
            ),
            project_id=(
                self._map_id(orm_model.project_id)
                if orm_model.project_id
                else None
            ),
            members=members,
            threads=threads,
            last_message_at=orm_model.last_message_at,
            is_archived=orm_model.is_archived,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: Chat) -> ChatORM:
        orm = ChatORM(
            id=self._map_uuid(aggregate.id),
            chat_type=aggregate.chat_type.value,
            name=aggregate.name,
            description=aggregate.description,
            icon=aggregate.icon,
            color=aggregate.color.value if aggregate.color else None,
            workspace_id=(
                self._map_uuid(aggregate.workspace_id)
                if aggregate.workspace_id
                else None
            ),
            project_id=(
                self._map_uuid(aggregate.project_id)
                if aggregate.project_id
                else None
            ),
            last_message_at=aggregate.last_message_at,
            is_archived=aggregate.is_archived,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
        orm.members = [self._member_to_orm(m, aggregate.id) for m in aggregate.members]
        orm.threads = [self._thread_to_orm(t, aggregate.id) for t in aggregate.threads]
        return orm

    def _member_to_orm(self, member: ChatMember, chat_id: Id) -> ChatMemberORM:
        return ChatMemberORM(
            id=self._map_uuid(member.id),
            chat_id=self._map_uuid(chat_id),
            user_id=self._map_uuid(member.user_id),
            role=member.role.value,
            joined_at=member.joined_at,
            last_read_at=member.last_read_at,
        )

    def _thread_to_orm(self, thread: Thread, chat_id: Id) -> ThreadORM:
        return ThreadORM(
            id=self._map_uuid(thread.id),
            chat_id=self._map_uuid(chat_id),
            parent_message_id=self._map_uuid(thread.parent_message_id),
            title=thread.title,
            is_resolved=thread.is_resolved,
            thread_created_at=thread.created_at,
        )
