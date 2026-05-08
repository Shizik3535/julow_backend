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


class CommentORM(BaseORMModel):
    """ORM-модель таблицы comments."""

    __tablename__ = "comments"
    __table_args__ = (
        Index(
            "ix_comments_target",
            "target_type",
            "target_id",
        ),
    )

    author_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(32), nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    parent_comment_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, nullable=True, index=True
    )

    # RichText (embedded VO)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_format: Mapped[str] = mapped_column(
        String(16), nullable=False, default="markdown"
    )

    is_pinned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True
    )

    reactions: Mapped[list["CommentReactionORM"]] = relationship(
        "CommentReactionORM",
        cascade="all, delete-orphan",
        lazy="selectin",
        back_populates="comment",
    )
    attachments: Mapped[list["CommentAttachmentORM"]] = relationship(
        "CommentAttachmentORM",
        cascade="all, delete-orphan",
        lazy="selectin",
        back_populates="comment",
    )


class CommentReactionORM(BaseORMModel):
    """ORM-модель таблицы comment_reactions."""

    __tablename__ = "comment_reactions"
    __table_args__ = (
        UniqueConstraint(
            "comment_id",
            "user_id",
            "emoji",
            name="uq_comment_reactions_comment_user_emoji",
        ),
    )

    comment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    emoji: Mapped[str] = mapped_column(String(64), nullable=False)
    reaction_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    comment: Mapped["CommentORM"] = relationship(
        "CommentORM", back_populates="reactions"
    )


class CommentAttachmentORM(BaseORMModel):
    """ORM-модель таблицы comment_attachments."""

    __tablename__ = "comment_attachments"

    comment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("comments.id", ondelete="CASCADE"),
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

    comment: Mapped["CommentORM"] = relationship(
        "CommentORM", back_populates="attachments"
    )
