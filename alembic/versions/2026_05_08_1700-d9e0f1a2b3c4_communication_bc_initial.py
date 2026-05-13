"""communication_bc_initial

Создаёт таблицы Communication BC: comments (с reactions/attachments),
chats (с members/threads), chat_messages (с reactions/attachments).

Revision ID: d9e0f1a2b3c4
Revises: 5cad42b1f3a7
Create Date: 2026-05-08 17:00:00.000000+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op


revision: str = "d9e0f1a2b3c4"
down_revision: str | Sequence[str] | None = "5cad42b1f3a7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""

    # ------------------------------------------------------------------
    # comments + comment_reactions + comment_attachments
    # ------------------------------------------------------------------

    op.create_table(
        "comments",
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("target_type", sa.String(length=32), nullable=False),
        sa.Column("target_id", sa.Uuid(), nullable=False),
        sa.Column("parent_comment_id", sa.Uuid(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("content_format", sa.String(length=16), nullable=False, server_default="markdown"),
        sa.Column("is_pinned", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_comments_author_id", "comments", ["author_id"])
    op.create_index("ix_comments_parent_comment_id", "comments", ["parent_comment_id"])
    op.create_index("ix_comments_is_deleted", "comments", ["is_deleted"])
    op.create_index("ix_comments_target", "comments", ["target_type", "target_id"])

    op.create_table(
        "comment_reactions",
        sa.Column("comment_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("emoji", sa.String(length=64), nullable=False),
        sa.Column("reaction_created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["comment_id"], ["comments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("comment_id", "user_id", "emoji", name="uq_comment_reactions_comment_user_emoji"),
    )
    op.create_index("ix_comment_reactions_comment_id", "comment_reactions", ["comment_id"])

    op.create_table(
        "comment_attachments",
        sa.Column("comment_id", sa.Uuid(), nullable=False),
        sa.Column("file_id", sa.Uuid(), nullable=False),
        sa.Column("attachment_type", sa.String(length=16), nullable=False),
        sa.Column("name", sa.String(length=512), nullable=False, server_default=""),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("url", sa.String(length=2048), nullable=True),
        sa.Column("preview_url", sa.String(length=2048), nullable=True),
        sa.Column("attachment_created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["comment_id"], ["comments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_comment_attachments_comment_id", "comment_attachments", ["comment_id"])

    # ------------------------------------------------------------------
    # chats + chat_members + chat_threads
    # ------------------------------------------------------------------

    op.create_table(
        "chats",
        sa.Column("chat_type", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("description", sa.String(length=1024), nullable=True),
        sa.Column("icon", sa.String(length=64), nullable=True),
        sa.Column("color", sa.String(length=16), nullable=True),
        sa.Column("workspace_id", sa.Uuid(), nullable=True),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chats_is_archived", "chats", ["is_archived"])
    op.create_index("ix_chats_workspace", "chats", ["workspace_id"])
    op.create_index("ix_chats_chat_type", "chats", ["chat_type"])

    op.create_table(
        "chat_members",
        sa.Column("chat_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["chat_id"], ["chats.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("chat_id", "user_id", name="uq_chat_members_chat_user"),
    )
    op.create_index("ix_chat_members_chat_id", "chat_members", ["chat_id"])
    op.create_index("ix_chat_members_user_id", "chat_members", ["user_id"])

    op.create_table(
        "chat_threads",
        sa.Column("chat_id", sa.Uuid(), nullable=False),
        sa.Column("parent_message_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("is_resolved", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("thread_created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["chat_id"], ["chats.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chat_threads_chat", "chat_threads", ["chat_id"])
    op.create_index("ix_chat_threads_parent_message", "chat_threads", ["parent_message_id"])

    # ------------------------------------------------------------------
    # chat_messages + chat_message_reactions + chat_message_attachments
    # ------------------------------------------------------------------

    op.create_table(
        "chat_messages",
        sa.Column("chat_id", sa.Uuid(), nullable=False),
        sa.Column("thread_id", sa.Uuid(), nullable=True),
        sa.Column("sender_id", sa.Uuid(), nullable=False),
        sa.Column("reply_to_id", sa.Uuid(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("content_format", sa.String(length=16), nullable=False, server_default="markdown"),
        sa.Column("message_type", sa.String(length=32), nullable=False),
        sa.Column("is_edited", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chat_messages_is_deleted", "chat_messages", ["is_deleted"])
    op.create_index("ix_chat_messages_chat_created", "chat_messages", ["chat_id", "created_at"])
    op.create_index("ix_chat_messages_thread", "chat_messages", ["thread_id"])
    op.create_index("ix_chat_messages_sender", "chat_messages", ["sender_id"])

    op.create_table(
        "chat_message_reactions",
        sa.Column("message_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("emoji", sa.String(length=64), nullable=False),
        sa.Column("reaction_created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["message_id"], ["chat_messages.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "message_id", "user_id", "emoji",
            name="uq_chat_message_reactions_msg_user_emoji",
        ),
    )
    op.create_index("ix_chat_message_reactions_message_id", "chat_message_reactions", ["message_id"])

    op.create_table(
        "chat_message_attachments",
        sa.Column("message_id", sa.Uuid(), nullable=False),
        sa.Column("file_id", sa.Uuid(), nullable=False),
        sa.Column("attachment_type", sa.String(length=16), nullable=False),
        sa.Column("name", sa.String(length=512), nullable=False, server_default=""),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("url", sa.String(length=2048), nullable=True),
        sa.Column("preview_url", sa.String(length=2048), nullable=True),
        sa.Column("attachment_created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["message_id"], ["chat_messages.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chat_message_attachments_message_id", "chat_message_attachments", ["message_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_chat_message_attachments_message_id", table_name="chat_message_attachments")
    op.drop_table("chat_message_attachments")
    op.drop_index("ix_chat_message_reactions_message_id", table_name="chat_message_reactions")
    op.drop_table("chat_message_reactions")
    op.drop_index("ix_chat_messages_sender", table_name="chat_messages")
    op.drop_index("ix_chat_messages_thread", table_name="chat_messages")
    op.drop_index("ix_chat_messages_chat_created", table_name="chat_messages")
    op.drop_index("ix_chat_messages_is_deleted", table_name="chat_messages")
    op.drop_table("chat_messages")
    op.drop_index("ix_chat_threads_parent_message", table_name="chat_threads")
    op.drop_index("ix_chat_threads_chat", table_name="chat_threads")
    op.drop_table("chat_threads")
    op.drop_index("ix_chat_members_user_id", table_name="chat_members")
    op.drop_index("ix_chat_members_chat_id", table_name="chat_members")
    op.drop_table("chat_members")
    op.drop_index("ix_chats_chat_type", table_name="chats")
    op.drop_index("ix_chats_workspace", table_name="chats")
    op.drop_index("ix_chats_is_archived", table_name="chats")
    op.drop_table("chats")
    op.drop_index("ix_comment_attachments_comment_id", table_name="comment_attachments")
    op.drop_table("comment_attachments")
    op.drop_index("ix_comment_reactions_comment_id", table_name="comment_reactions")
    op.drop_table("comment_reactions")
    op.drop_index("ix_comments_target", table_name="comments")
    op.drop_index("ix_comments_is_deleted", table_name="comments")
    op.drop_index("ix_comments_parent_comment_id", table_name="comments")
    op.drop_index("ix_comments_author_id", table_name="comments")
    op.drop_table("comments")
