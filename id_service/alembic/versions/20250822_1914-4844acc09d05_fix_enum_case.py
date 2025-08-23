"""fix enum case

Revision ID: 4844acc09d05
Revises: 0001_initial
Create Date: 2025-08-22 19:14:18.705987

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4844acc09d05'
down_revision = '0001_initial'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Переименовать значения enum'ов, если они ещё в UPPERCASE
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = 'clienttype' AND e.enumlabel = 'PUBLIC'
        ) THEN
            ALTER TYPE clienttype RENAME VALUE 'PUBLIC' TO 'public';
        END IF;
    END$$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = 'tokenauthmethod' AND e.enumlabel = 'NONE'
        ) THEN
            ALTER TYPE tokenauthmethod RENAME VALUE 'NONE' TO 'none';
        END IF;
        IF EXISTS (
            SELECT 1 FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = 'tokenauthmethod' AND e.enumlabel = 'CLIENT_SECRET_POST'
        ) THEN
            ALTER TYPE tokenauthmethod RENAME VALUE 'CLIENT_SECRET_POST' TO 'client_secret_post';
        END IF;
        IF EXISTS (
            SELECT 1 FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = 'tokenauthmethod' AND e.enumlabel = 'CLIENT_SECRET_BASIC'
        ) THEN
            ALTER TYPE tokenauthmethod RENAME VALUE 'CLIENT_SECRET_BASIC' TO 'client_secret_basic';
        END IF;
    END$$;
    """)

    # Обновить server_default'ы
    op.alter_column(
        "clients", "type",
        server_default=sa.text("'public'::clienttype"),
        existing_type=sa.Enum(name="clienttype"),
    )
    op.alter_column(
        "clients", "token_endpoint_auth_method",
        server_default=sa.text("'none'::tokenauthmethod"),
        existing_type=sa.Enum(name="tokenauthmethod"),
    )


def downgrade() -> None:
    # Откатить значения enum'ов обратно в UPPERCASE (на случай даунгрейда)
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = 'clienttype' AND e.enumlabel = 'public'
        ) THEN
            ALTER TYPE clienttype RENAME VALUE 'public' TO 'PUBLIC';
        END IF;
    END$$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = 'tokenauthmethod' AND e.enumlabel = 'client_secret_basic'
        ) THEN
            ALTER TYPE tokenauthmethod RENAME VALUE 'client_secret_basic' TO 'CLIENT_SECRET_BASIC';
        END IF;
        IF EXISTS (
            SELECT 1 FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = 'tokenauthmethod' AND e.enumlabel = 'client_secret_post'
        ) THEN
            ALTER TYPE tokenauthmethod RENAME VALUE 'client_secret_post' TO 'CLIENT_SECRET_POST';
        END IF;
        IF EXISTS (
            SELECT 1 FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = 'tokenauthmethod' AND e.enumlabel = 'none'
        ) THEN
            ALTER TYPE tokenauthmethod RENAME VALUE 'none' TO 'NONE';
        END IF;
    END$$;
    """)

    op.alter_column(
        "clients", "type",
        server_default=sa.text("'PUBLIC'::clienttype"),
        existing_type=sa.Enum(name="clienttype"),
    )
    op.alter_column(
        "clients", "token_endpoint_auth_method",
        server_default=sa.text("'NONE'::tokenauthmethod"),
        existing_type=sa.Enum(name="tokenauthmethod"),
    )
