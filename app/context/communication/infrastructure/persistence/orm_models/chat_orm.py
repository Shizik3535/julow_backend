from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class ChatORM(BaseORMModel):
    """ORM-модель таблицы chats."""

    __tablename__ = "chats"
    __table_args__ = (
        Index("ix_chats_workspace", "workspace_id"),
        Index("ix_chats_chat_type", "chat_type"),
    )

    chat_type: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(64), nullable=True)
    color: Mapped[str | None] = mapped_column(String(16), nullable=True)
    workspace_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)

    last_message_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_archived: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True
    )

    members: Mapped[list["ChatMemberORM"]] = relationship(
        "ChatMemberORM",
        cascade="all, delete-orphan",
        lazy="selectin",
        back_populates="chat",
    )
    threads: Mapped[list["ThreadORM"]] = relationship(
        "ThreadORM",
        cascade="all, delete-orphan",
        lazy="selectin",
        back_populates="chat",
    )


class ChatMemberORM(BaseORMModel):
    """ORM-модель таблицы chat_members."""

    __tablename__ = "chat_members"
    __table_args__ = (
        UniqueConstraint(
            "chat_id",
            "user_id",
            name="uq_chat_members_chat_user",
        ),
    )

    chat_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    chat: Mapped["ChatORM"] = relationship("ChatORM", back_populates="members")


class ThreadORM(BaseORMModel):
    """ORM-модель таблицы chat_threads."""

    __tablename__ = "chat_threads"
    __table_args__ = (
        Index("ix_chat_threads_chat", "chat_id"),
        Index("ix_chat_threads_parent_message", "parent_message_id"),
    )

    chat_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent_message_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    thread_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    chat: Mapped["ChatORM"] = relationship("ChatORM", back_populates="threads")
