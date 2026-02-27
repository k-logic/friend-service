"""split_accounts_to_users_and_staff

Revision ID: d4e5f6a7b8c9
Revises: 0e08274ff9c4
Create Date: 2026-02-27 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "0e08274ff9c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ========================================
    # 1. users テーブル作成
    # ========================================
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("credit_balance", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "status",
            sa.Enum("active", "suspended", name="userstatus"),
            server_default="active",
            nullable=False,
        ),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    # ========================================
    # 2. staff_members テーブル作成
    # ========================================
    op.create_table(
        "staff_members",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("staff", "admin", name="staffrole"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("active", "suspended", name="staffstatus"),
            server_default="active",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_staff_members_email"), "staff_members", ["email"], unique=True
    )

    # ========================================
    # 3. accounts からデータをコピー
    # ========================================
    op.execute(
        """
        INSERT INTO users (id, email, display_name, hashed_password, credit_balance, status, avatar_url, created_at, updated_at)
        SELECT id, email, display_name, hashed_password, credit_balance,
               status::text::userstatus, avatar_url, created_at, updated_at
        FROM accounts WHERE role = 'user'
    """
    )
    op.execute(
        """
        INSERT INTO staff_members (id, email, display_name, hashed_password, role, status, created_at, updated_at)
        SELECT id, email, display_name, hashed_password,
               role::text::staffrole, status::text::staffstatus, created_at, updated_at
        FROM accounts WHERE role IN ('staff', 'admin')
    """
    )

    # シーケンスのリセット
    op.execute(
        "SELECT setval(pg_get_serial_sequence('users', 'id'), COALESCE((SELECT MAX(id) FROM users), 1))"
    )
    op.execute(
        "SELECT setval(pg_get_serial_sequence('staff_members', 'id'), COALESCE((SELECT MAX(id) FROM staff_members), 1))"
    )

    # ========================================
    # 4. FK 変更前に、スタッフID を参照する孤立データを削除
    #    （通知・問い合わせ等はユーザーのみのテーブルだが、
    #     旧スキーマでは accounts.id を共有していたため）
    # ========================================
    op.execute("DELETE FROM notifications WHERE account_id NOT IN (SELECT id FROM users)")
    op.execute("DELETE FROM inquiries WHERE account_id NOT IN (SELECT id FROM users)")
    op.execute("DELETE FROM footprints WHERE visitor_account_id NOT IN (SELECT id FROM users)")
    op.execute("DELETE FROM likes WHERE user_account_id NOT IN (SELECT id FROM users)")
    op.execute("DELETE FROM sessions WHERE user_account_id NOT IN (SELECT id FROM users)")
    op.execute("DELETE FROM age_verifications WHERE account_id NOT IN (SELECT id FROM users)")

    # ========================================
    # 5. 各テーブルの FK 制約削除 → カラムリネーム → 新 FK 制約作成
    # ========================================

    # --- sessions ---
    op.drop_constraint("sessions_user_account_id_fkey", "sessions", type_="foreignkey")
    op.drop_index("ix_sessions_user_account_id", table_name="sessions")
    op.alter_column("sessions", "user_account_id", new_column_name="user_id")
    op.create_foreign_key(
        "sessions_user_id_fkey", "sessions", "users", ["user_id"], ["id"]
    )
    op.create_index(op.f("ix_sessions_user_id"), "sessions", ["user_id"])

    # --- personas ---
    op.drop_constraint(
        "personas_staff_account_id_fkey", "personas", type_="foreignkey"
    )
    op.drop_index("ix_personas_staff_account_id", table_name="personas")
    op.alter_column("personas", "staff_account_id", new_column_name="staff_id")
    op.create_foreign_key(
        "personas_staff_id_fkey", "personas", "staff_members", ["staff_id"], ["id"]
    )
    op.create_index(op.f("ix_personas_staff_id"), "personas", ["staff_id"])

    # --- likes ---
    op.drop_constraint("likes_user_account_id_fkey", "likes", type_="foreignkey")
    op.drop_index("ix_likes_user_account_id", table_name="likes")
    op.drop_constraint("uq_likes_user_persona", "likes", type_="unique")
    op.alter_column("likes", "user_account_id", new_column_name="user_id")
    op.create_foreign_key(
        "likes_user_id_fkey", "likes", "users", ["user_id"], ["id"]
    )
    op.create_index(op.f("ix_likes_user_id"), "likes", ["user_id"])
    op.create_unique_constraint(
        "uq_likes_user_persona", "likes", ["user_id", "persona_id"]
    )

    # --- footprints ---
    op.drop_constraint(
        "footprints_visitor_account_id_fkey", "footprints", type_="foreignkey"
    )
    op.drop_index("ix_footprints_visitor_account_id", table_name="footprints")
    op.drop_constraint(
        "uq_footprints_visitor_persona", "footprints", type_="unique"
    )
    op.alter_column("footprints", "visitor_account_id", new_column_name="user_id")
    op.create_foreign_key(
        "footprints_user_id_fkey", "footprints", "users", ["user_id"], ["id"]
    )
    op.create_index(op.f("ix_footprints_user_id"), "footprints", ["user_id"])
    op.create_unique_constraint(
        "uq_footprints_user_persona", "footprints", ["user_id", "persona_id"]
    )

    # --- notifications ---
    op.drop_constraint(
        "notifications_account_id_fkey", "notifications", type_="foreignkey"
    )
    op.drop_index("ix_notifications_account_id", table_name="notifications")
    op.alter_column("notifications", "account_id", new_column_name="user_id")
    op.create_foreign_key(
        "notifications_user_id_fkey", "notifications", "users", ["user_id"], ["id"]
    )
    op.create_index(
        op.f("ix_notifications_user_id"), "notifications", ["user_id"]
    )

    # --- inquiries ---
    op.drop_constraint(
        "inquiries_account_id_fkey", "inquiries", type_="foreignkey"
    )
    op.drop_index("ix_inquiries_account_id", table_name="inquiries")
    op.alter_column("inquiries", "account_id", new_column_name="user_id")
    op.create_foreign_key(
        "inquiries_user_id_fkey", "inquiries", "users", ["user_id"], ["id"]
    )
    op.create_index(op.f("ix_inquiries_user_id"), "inquiries", ["user_id"])

    # --- age_verifications ---
    op.drop_constraint(
        "age_verifications_account_id_fkey", "age_verifications", type_="foreignkey"
    )
    op.drop_constraint(
        "age_verifications_reviewer_id_fkey", "age_verifications", type_="foreignkey"
    )
    op.drop_index("ix_age_verifications_account_id", table_name="age_verifications")
    op.alter_column("age_verifications", "account_id", new_column_name="user_id")
    op.create_foreign_key(
        "age_verifications_user_id_fkey",
        "age_verifications",
        "users",
        ["user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "age_verifications_reviewer_id_fkey",
        "age_verifications",
        "staff_members",
        ["reviewer_id"],
        ["id"],
    )
    op.create_index(
        op.f("ix_age_verifications_user_id"), "age_verifications", ["user_id"]
    )

    # --- invitation_tokens ---
    op.drop_constraint(
        "invitation_tokens_created_by_fkey", "invitation_tokens", type_="foreignkey"
    )
    op.drop_constraint(
        "invitation_tokens_used_by_fkey", "invitation_tokens", type_="foreignkey"
    )
    op.create_foreign_key(
        "invitation_tokens_created_by_fkey",
        "invitation_tokens",
        "staff_members",
        ["created_by"],
        ["id"],
    )
    op.create_foreign_key(
        "invitation_tokens_used_by_fkey",
        "invitation_tokens",
        "users",
        ["used_by"],
        ["id"],
    )

    # --- templates ---
    op.drop_constraint(
        "templates_staff_account_id_fkey", "templates", type_="foreignkey"
    )
    op.drop_index("ix_templates_staff_account_id", table_name="templates")
    op.alter_column("templates", "staff_account_id", new_column_name="staff_id")
    op.create_foreign_key(
        "templates_staff_id_fkey", "templates", "staff_members", ["staff_id"], ["id"]
    )
    op.create_index(op.f("ix_templates_staff_id"), "templates", ["staff_id"])

    # ========================================
    # 5. accounts テーブル削除
    # ========================================
    op.drop_index(op.f("ix_accounts_email"), table_name="accounts")
    op.drop_table("accounts")

    # ========================================
    # 6. 旧 enum 型の削除
    # ========================================
    op.execute("DROP TYPE accountrole")
    op.execute("DROP TYPE accountstatus")


def downgrade() -> None:
    # ========================================
    # 逆順で accounts テーブルを復元
    # ========================================

    # 旧 enum 型の復元
    op.execute("CREATE TYPE accountrole AS ENUM ('user', 'staff', 'admin')")
    op.execute("CREATE TYPE accountstatus AS ENUM ('active', 'suspended')")

    # accounts テーブル再作成
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("credit_balance", sa.Integer(), nullable=False),
        sa.Column(
            "role",
            sa.Enum("user", "staff", "admin", name="accountrole", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("active", "suspended", name="accountstatus", create_type=False),
            nullable=False,
        ),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_accounts_email"), "accounts", ["email"], unique=True)

    # データ復元: users → accounts
    op.execute(
        """
        INSERT INTO accounts (id, email, display_name, hashed_password, credit_balance, role, status, avatar_url, created_at, updated_at)
        SELECT id, email, display_name, hashed_password, credit_balance,
               'user'::accountrole, status::text::accountstatus, avatar_url, created_at, updated_at
        FROM users
    """
    )
    # データ復元: staff_members → accounts
    op.execute(
        """
        INSERT INTO accounts (id, email, display_name, hashed_password, credit_balance, role, status, avatar_url, created_at, updated_at)
        SELECT id, email, display_name, hashed_password, 0,
               role::text::accountrole, status::text::accountstatus, NULL, created_at, updated_at
        FROM staff_members
    """
    )
    op.execute(
        "SELECT setval(pg_get_serial_sequence('accounts', 'id'), COALESCE((SELECT MAX(id) FROM accounts), 1))"
    )

    # --- templates ---
    op.drop_constraint("templates_staff_id_fkey", "templates", type_="foreignkey")
    op.drop_index(op.f("ix_templates_staff_id"), table_name="templates")
    op.alter_column("templates", "staff_id", new_column_name="staff_account_id")
    op.create_foreign_key(
        "templates_staff_account_id_fkey",
        "templates",
        "accounts",
        ["staff_account_id"],
        ["id"],
    )
    op.create_index(
        op.f("ix_templates_staff_account_id"), "templates", ["staff_account_id"]
    )

    # --- invitation_tokens ---
    op.drop_constraint(
        "invitation_tokens_created_by_fkey", "invitation_tokens", type_="foreignkey"
    )
    op.drop_constraint(
        "invitation_tokens_used_by_fkey", "invitation_tokens", type_="foreignkey"
    )
    op.create_foreign_key(
        "invitation_tokens_created_by_fkey",
        "invitation_tokens",
        "accounts",
        ["created_by"],
        ["id"],
    )
    op.create_foreign_key(
        "invitation_tokens_used_by_fkey",
        "invitation_tokens",
        "accounts",
        ["used_by"],
        ["id"],
    )

    # --- age_verifications ---
    op.drop_constraint(
        "age_verifications_user_id_fkey", "age_verifications", type_="foreignkey"
    )
    op.drop_constraint(
        "age_verifications_reviewer_id_fkey", "age_verifications", type_="foreignkey"
    )
    op.drop_index(op.f("ix_age_verifications_user_id"), table_name="age_verifications")
    op.alter_column("age_verifications", "user_id", new_column_name="account_id")
    op.create_foreign_key(
        "age_verifications_account_id_fkey",
        "age_verifications",
        "accounts",
        ["account_id"],
        ["id"],
    )
    op.create_foreign_key(
        "age_verifications_reviewer_id_fkey",
        "age_verifications",
        "accounts",
        ["reviewer_id"],
        ["id"],
    )
    op.create_index(
        op.f("ix_age_verifications_account_id"),
        "age_verifications",
        ["account_id"],
    )

    # --- inquiries ---
    op.drop_constraint("inquiries_user_id_fkey", "inquiries", type_="foreignkey")
    op.drop_index(op.f("ix_inquiries_user_id"), table_name="inquiries")
    op.alter_column("inquiries", "user_id", new_column_name="account_id")
    op.create_foreign_key(
        "inquiries_account_id_fkey", "inquiries", "accounts", ["account_id"], ["id"]
    )
    op.create_index(op.f("ix_inquiries_account_id"), "inquiries", ["account_id"])

    # --- notifications ---
    op.drop_constraint(
        "notifications_user_id_fkey", "notifications", type_="foreignkey"
    )
    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.alter_column("notifications", "user_id", new_column_name="account_id")
    op.create_foreign_key(
        "notifications_account_id_fkey",
        "notifications",
        "accounts",
        ["account_id"],
        ["id"],
    )
    op.create_index(
        op.f("ix_notifications_account_id"), "notifications", ["account_id"]
    )

    # --- footprints ---
    op.drop_constraint("footprints_user_id_fkey", "footprints", type_="foreignkey")
    op.drop_index(op.f("ix_footprints_user_id"), table_name="footprints")
    op.drop_constraint("uq_footprints_user_persona", "footprints", type_="unique")
    op.alter_column("footprints", "user_id", new_column_name="visitor_account_id")
    op.create_foreign_key(
        "footprints_visitor_account_id_fkey",
        "footprints",
        "accounts",
        ["visitor_account_id"],
        ["id"],
    )
    op.create_index(
        op.f("ix_footprints_visitor_account_id"),
        "footprints",
        ["visitor_account_id"],
    )
    op.create_unique_constraint(
        "uq_footprints_visitor_persona",
        "footprints",
        ["visitor_account_id", "persona_id"],
    )

    # --- likes ---
    op.drop_constraint("likes_user_id_fkey", "likes", type_="foreignkey")
    op.drop_index(op.f("ix_likes_user_id"), table_name="likes")
    op.drop_constraint("uq_likes_user_persona", "likes", type_="unique")
    op.alter_column("likes", "user_id", new_column_name="user_account_id")
    op.create_foreign_key(
        "likes_user_account_id_fkey", "likes", "accounts", ["user_account_id"], ["id"]
    )
    op.create_index(op.f("ix_likes_user_account_id"), "likes", ["user_account_id"])
    op.create_unique_constraint(
        "uq_likes_user_persona", "likes", ["user_account_id", "persona_id"]
    )

    # --- personas ---
    op.drop_constraint("personas_staff_id_fkey", "personas", type_="foreignkey")
    op.drop_index(op.f("ix_personas_staff_id"), table_name="personas")
    op.alter_column("personas", "staff_id", new_column_name="staff_account_id")
    op.create_foreign_key(
        "personas_staff_account_id_fkey",
        "personas",
        "accounts",
        ["staff_account_id"],
        ["id"],
    )
    op.create_index(
        op.f("ix_personas_staff_account_id"), "personas", ["staff_account_id"]
    )

    # --- sessions ---
    op.drop_constraint("sessions_user_id_fkey", "sessions", type_="foreignkey")
    op.drop_index(op.f("ix_sessions_user_id"), table_name="sessions")
    op.alter_column("sessions", "user_id", new_column_name="user_account_id")
    op.create_foreign_key(
        "sessions_user_account_id_fkey",
        "sessions",
        "accounts",
        ["user_account_id"],
        ["id"],
    )
    op.create_index(
        op.f("ix_sessions_user_account_id"), "sessions", ["user_account_id"]
    )

    # users / staff_members テーブル削除
    op.drop_index(op.f("ix_staff_members_email"), table_name="staff_members")
    op.drop_table("staff_members")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    # 新しい enum 型の削除
    op.execute("DROP TYPE userstatus")
    op.execute("DROP TYPE staffrole")
    op.execute("DROP TYPE staffstatus")
