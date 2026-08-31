"""001_initial_schema - 初始建表（29 表，与 /design/02-database/README.md 对齐）

Revision ID: 001
Revises: None
Create Date: 2026-08-20
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ========== RBAC 域 (10 表) ==========
    op.create_table(
        "sys_dept",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("parent_id", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("leader_user_id", sa.BigInteger(), nullable=True),
        sa.Column("sort", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
    )
    op.create_index("idx_sys_dept_parent_id", "sys_dept", ["parent_id"])

    op.create_table(
        "sys_user",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("dept_id", sa.BigInteger(), nullable=True),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("nickname", sa.String(64), nullable=False, server_default=""),
        sa.Column("email", sa.String(128), nullable=False, server_default=""),
        sa.Column("phone", sa.String(32), nullable=False, server_default=""),
        sa.Column("avatar_url", sa.String(512), nullable=False, server_default=""),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1", comment="1=启用 2=禁用"),
        sa.Column("mfa_secret_enc", sa.VARBINARY(255), nullable=True),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username", name="uk_sys_user_username"),
        mysql_charset="utf8mb4",
    )
    op.create_index("idx_sys_user_dept_id", "sys_user", ["dept_id"])

    op.create_table(
        "sys_role",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("role_type", sa.SmallInteger(), nullable=False, server_default="3", comment="1=内置系统 2=业务预置 3=自定义"),
        sa.Column("data_scope", sa.SmallInteger(), nullable=False, server_default="4", comment="1=ALL 2=DEPT 3=DEPT_AND_CHILD 4=SELF 5=CUSTOM"),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("remark", sa.String(255), nullable=True),
        sa.Column("sort", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uk_sys_role_code"),
        mysql_charset="utf8mb4",
    )

    op.create_table(
        "sys_permission",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("menu_id", sa.BigInteger(), nullable=True),
        sa.Column("code", sa.String(128), nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("type", sa.SmallInteger(), nullable=False, server_default="3", comment="1=menu 2=btn 3=api"),
        sa.Column("api_method", sa.String(8), nullable=True),
        sa.Column("api_path", sa.String(255), nullable=True),
        sa.Column("sort", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uk_sys_permission_code"),
        mysql_charset="utf8mb4",
    )

    op.create_table(
        "sys_user_role",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("role_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "role_id", name="uk_user_role"),
        mysql_charset="utf8mb4",
    )

    op.create_table(
        "sys_role_perm",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("role_id", sa.BigInteger(), nullable=False),
        sa.Column("perm_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("role_id", "perm_id", name="uk_role_perm"),
        mysql_charset="utf8mb4",
    )

    op.create_table(
        "sys_role_data_scope",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("role_id", sa.BigInteger(), nullable=False),
        sa.Column("dept_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("role_id", "dept_id", name="uk_scope"),
        mysql_charset="utf8mb4",
    )

    op.create_table(
        "sys_menu",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("parent_id", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("path", sa.String(128), nullable=False, server_default=""),
        sa.Column("component", sa.String(255), nullable=True),
        sa.Column("icon", sa.String(64), nullable=True),
        sa.Column("perm_code", sa.String(128), nullable=True),
        sa.Column("sort", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("visible", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
    )

    op.create_table(
        "sys_audit_log",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("resource", sa.String(128), nullable=False, server_default=""),
        sa.Column("detail", sa.JSON(), nullable=True),
        sa.Column("ip", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
    )
    op.create_index("idx_audit_user", "sys_audit_log", ["user_id", "created_at"])
    op.create_index("idx_audit_action", "sys_audit_log", ["action", "created_at"])

    op.create_table(
        "sys_login_log",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("login_type", sa.String(16), nullable=False, server_default="password"),
        sa.Column("ip", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(512), nullable=True),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1", comment="1=成功 2=失败"),
        sa.Column("msg", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
    )

    # ========== 知识库域 (5 表) ==========
    op.create_table(
        "kb_category",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("parent_id", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("sort", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
    )

    op.create_table(
        "kb_document",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("category_id", sa.BigInteger(), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("file_type", sa.String(16), nullable=False),
        sa.Column("file_url", sa.String(512), nullable=False, server_default=""),
        sa.Column("file_hash", sa.String(64), nullable=False, server_default=""),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1", comment="1=draft 2=pending_review 3=published 4=offline"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("file_hash", name="uk_doc_hash"),
        mysql_charset="utf8mb4",
    )
    op.create_index("idx_doc_category", "kb_document", ["category_id", "status"])

    op.create_table(
        "kb_chunk",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("doc_id", sa.BigInteger(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1", comment="1=active 2=archived"),
        sa.Column("embedding_status", sa.SmallInteger(), nullable=False, server_default="1", comment="1=pending 2=done 3=failed"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("doc_id", "chunk_index", name="uk_chunk_doc_idx"),
        mysql_charset="utf8mb4",
    )
    op.create_index("idx_chunk_embedding_status", "kb_chunk", ["embedding_status"])

    op.create_table(
        "kb_qa_pair",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("doc_id", sa.BigInteger(), nullable=True),
        sa.Column("chunk_id", sa.BigInteger(), nullable=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("hit_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
    )

    op.create_table(
        "kb_import_task",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("doc_id", sa.BigInteger(), nullable=False),
        sa.Column("task_type", sa.String(16), nullable=False, comment="parse/chunk/embed/index"),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending", comment="pending/running/done/failed"),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_msg", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
    )

    # ========== 对话域 (5 表) ==========
    op.create_table(
        "chat_session",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("customer_id", sa.String(64), nullable=False),
        sa.Column("source", sa.String(16), nullable=False, server_default="web", comment="web/h5/mini/wechat"),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1", comment="1=active 2=transferred 3=closed"),
        sa.Column("rating", sa.SmallInteger(), nullable=True),
        sa.Column("model_config_id", sa.BigInteger(), nullable=True),
        sa.Column("transferred_reason", sa.String(255), nullable=True),
        sa.Column("last_msg_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
    )
    op.create_index("idx_session_customer", "chat_session", ["customer_id", "status", "last_msg_at"])
    op.create_index("idx_session_status_time", "chat_session", ["status", "created_at"])

    op.create_table(
        "chat_message",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.BigInteger(), nullable=False),
        sa.Column("role", sa.String(16), nullable=False, comment="user/assistant/system/agent"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("msg_type", sa.String(16), nullable=False, server_default="text", comment="text/card/transfer/rating"),
        sa.Column("tokens", sa.Integer(), nullable=True),
        sa.Column("model", sa.String(64), nullable=True),
        sa.Column("retrieval_ids", sa.JSON(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
    )
    op.create_index("idx_msg_session", "chat_message", ["session_id", "created_at"])
    op.create_index("idx_msg_created", "chat_message", ["created_at"])

    op.create_table(
        "chat_retrieval_log",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("message_id", sa.BigInteger(), nullable=False),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("topk_scores", sa.JSON(), nullable=True),
        sa.Column("threshold", sa.Float(), nullable=True),
        sa.Column("hit_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rerank_used", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
    )
    op.create_index("idx_retrieval_message", "chat_retrieval_log", ["message_id"])
    op.create_index("idx_retrieval_time", "chat_retrieval_log", ["created_at"])

    op.create_table(
        "chat_feedback",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("message_id", sa.BigInteger(), nullable=False),
        sa.Column("session_id", sa.BigInteger(), nullable=False),
        sa.Column("feedback_type", sa.SmallInteger(), nullable=False, comment="1=点赞 2=点踩"),
        sa.Column("reason", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
    )
    op.create_index("idx_feedback_message", "chat_feedback", ["message_id"])

    op.create_table(
        "chat_quick_reply",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("scene", sa.String(32), nullable=False, server_default="", comment="greeting/refund/shipping"),
        sa.Column("title", sa.String(64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("sort", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
    )

    # ========== 工单与坐席域 (5 表) ==========
    op.create_table(
        "agent_group",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("sort", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
    )

    op.create_table(
        "agent_profile",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("group_id", sa.BigInteger(), nullable=True),
        sa.Column("agent_no", sa.String(32), nullable=False),
        sa.Column("skill_tags", sa.JSON(), nullable=True),
        sa.Column("max_concurrency", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("online_status", sa.SmallInteger(), nullable=False, server_default="3", comment="1=在线 2=忙碌 3=离线"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uk_agent_user"),
        sa.UniqueConstraint("agent_no", name="uk_agent_no"),
        mysql_charset="utf8mb4",
    )

    op.create_table(
        "human_ticket",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.BigInteger(), nullable=False),
        sa.Column("ticket_no", sa.String(32), nullable=False),
        sa.Column("reason", sa.String(255), nullable=True),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1", comment="1=pending 2=assigned 3=processing 4=resolved 5=closed"),
        sa.Column("priority", sa.SmallInteger(), nullable=False, server_default="2", comment="1=低 2=中 3=高 4=紧急"),
        sa.Column("assignee_id", sa.BigInteger(), nullable=True),
        sa.Column("group_id", sa.BigInteger(), nullable=True),
        sa.Column("snapshot", sa.JSON(), nullable=True),
        sa.Column("first_response_at", sa.DateTime(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ticket_no", name="uk_ticket_no"),
        mysql_charset="utf8mb4",
    )
    op.create_index("idx_ticket_assignee", "human_ticket", ["assignee_id", "status"])
    op.create_index("idx_ticket_status", "human_ticket", ["status", "priority", "created_at"])

    op.create_table(
        "ticket_comment",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("ticket_id", sa.BigInteger(), nullable=False),
        sa.Column("author_id", sa.BigInteger(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_internal", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
    )

    op.create_table(
        "ticket_assign_log",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("ticket_id", sa.BigInteger(), nullable=False),
        sa.Column("from_agent_id", sa.BigInteger(), nullable=True),
        sa.Column("to_agent_id", sa.BigInteger(), nullable=True),
        sa.Column("action", sa.String(16), nullable=False, comment="assign/transfer/claim/escalate/close"),
        sa.Column("operator_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
    )

    # ========== AI 配置域 (3 表) ==========
    op.create_table(
        "sys_model_config",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("model_type", sa.String(16), nullable=False, comment="llm/embedding/rerank"),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("model_name", sa.String(64), nullable=False),
        sa.Column("endpoint", sa.String(512), nullable=False, server_default=""),
        sa.Column("api_key_enc", sa.VARBINARY(512), nullable=True),
        sa.Column("params", sa.JSON(), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
    )

    op.create_table(
        "sys_prompt_template",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("scene", sa.String(32), nullable=False, comment="chat_hit/chat_miss/rewrite/summarize"),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("variables", sa.JSON(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
    )

    op.create_table(
        "kb_retrieval_config",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("scope", sa.String(16), nullable=False, comment="global/category/doc"),
        sa.Column("target_id", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("topk", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("score_threshold", sa.Float(), nullable=False, server_default="0.78"),
        sa.Column("rerank_enabled", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("rerank_model_id", sa.BigInteger(), nullable=True),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
    )

    # ========== 统计域 (1 表) ==========
    op.create_table(
        "stat_daily",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("stat_date", sa.Date(), nullable=False),
        sa.Column("session_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("message_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ticket_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("transfer_rate", sa.Float(), nullable=False, server_default="0"),
        sa.Column("hit_rate", sa.Float(), nullable=False, server_default="0"),
        sa.Column("avg_rating", sa.Float(), nullable=True),
        sa.Column("avg_first_response_ms", sa.Integer(), nullable=True),
        sa.Column("llm_tokens_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stat_date", name="uk_stat_date"),
        mysql_charset="utf8mb4",
    )


def downgrade() -> None:
    op.drop_table("stat_daily")
    op.drop_table("kb_retrieval_config")
    op.drop_table("sys_prompt_template")
    op.drop_table("sys_model_config")
    op.drop_table("ticket_assign_log")
    op.drop_table("ticket_comment")
    op.drop_table("human_ticket")
    op.drop_table("agent_profile")
    op.drop_table("agent_group")
    op.drop_table("chat_quick_reply")
    op.drop_table("chat_feedback")
    op.drop_table("chat_retrieval_log")
    op.drop_table("chat_message")
    op.drop_table("chat_session")
    op.drop_table("kb_import_task")
    op.drop_table("kb_qa_pair")
    op.drop_table("kb_chunk")
    op.drop_table("kb_document")
    op.drop_table("kb_category")
    op.drop_table("sys_login_log")
    op.drop_table("sys_audit_log")
    op.drop_table("sys_menu")
    op.drop_table("sys_role_data_scope")
    op.drop_table("sys_role_perm")
    op.drop_table("sys_user_role")
    op.drop_table("sys_permission")
    op.drop_table("sys_role")
    op.drop_table("sys_user")
    op.drop_table("sys_dept")