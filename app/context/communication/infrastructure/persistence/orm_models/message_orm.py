from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class MessageORM(BaseORMModel):
    """ORM-модель таблицы chat_messages."""

    __tablename__ = "chat_messages"
    __table_args__ = (
        Index("ix_chat_messages_chat_created", "chat_id", "created_at"),
        Index("ix_chat_messages_thread", "thread_id"),
        Index("ix_chat_messages_sender", "sender_id"),
    )

    chat_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    thread_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    sender_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    reply_to_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)

    # RichText (embedded VO)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_format: Mapped[str] = mapped_column(
        String(16), nullable=False, default="markdown"
    )

    message_type: Mapped[str] = mapped_column(String(32), nullable=False)
    is_edited: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True
    )

    reactions: Mapped[list["MessageReactionORM"]] = relationship(
        "MessageReactionORM",
        cascade="all, delete-orphan",
        lazy="selectin",
        back_populates="message",
    )
    attachments: Mapped[list["MessageAttachmentORM"]] = relationship(
        "MessageAttachmentORM",
        cascade="all, delete-orphan",
        lazy="selectin",
        back_populates="message",
    )


class MessageReactionORM(BaseORMModel):
    """ORM-модель таблицы chat_message_reactions."""

    __tablename__ = "chat_message_reactions"
    __table_args__ = (
        UniqueConstraint(
            "message_id",
            "user_id",
            "emoji",
            name="uq_chat_message_reactions_msg_user_emoji",
        ),
    )

    message_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("chat_messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    emoji: Mapped[str] = mapped_column(String(64), nullable=False)
    reaction_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    message: Mapped["MessageORM"] = relationship(
        "MessageORM", back_populates="reactions"
    )


class MessageAttachmentORM(BaseORMModel):
    """ORM-модель таблицы chat_message_attachments."""

    __tablename__ = "chat_message_attachments"

    message_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("chat_messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    attachment_type: Mapped[str] = mapped_column(String(16), nullable=False)
    name: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    preview_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    attachment_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    message: Mapped["MessageORM"] = relationship(
        "MessageORM", back_populates="attachments"
    )
