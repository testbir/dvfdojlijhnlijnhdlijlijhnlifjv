"""rename enum values to lowercase & fix defaults

Revision ID: 624ce4ceb2ee
Revises: f94c88b39bdb
Create Date: 2025-08-22 16:40:42.534939

"""

# id_service/alembic/versions/20250822_1640-624ce4ceb2ee_rename_enum_values_to_lowercase_fix_.py
from alembic import op
import sqlalchemy as sa

revision = "624ce4ceb2ee"
down_revision = "f94c88b39bdb"
branch_labels = None
depends_on = None

def upgrade() -> None:
    # убрать дефолты на время изменения enum
    op.alter_column("clients", "type", server_default=None)
    op.alter_column("clients", "token_endpoint_auth_method", server_default=None)

    # clienttype
    op.execute("""
    DO $$
    BEGIN
      IF EXISTS (
        SELECT 1 FROM pg_type t
        JOIN pg_enum e ON e.enumtypid = t.oid
        WHERE t.typname = 'clienttype' AND e.enumlabel = 'PUBLIC'
      ) THEN
        ALTER TYPE clienttype RENAME VALUE 'PUBLIC' TO 'public';
      END IF;

      IF EXISTS (
        SELECT 1 FROM pg_type t
        JOIN pg_enum e ON e.enumtypid = t.oid
        WHERE t.typname = 'clienttype' AND e.enumlabel = 'CONFIDENTIAL'
      ) THEN
        ALTER TYPE clienttype RENAME VALUE 'CONFIDENTIAL' TO 'confidential';
      END IF;
    END$$;
    """)

    # tokenauthmethod
    op.execute("""
    DO $$
    BEGIN
      IF EXISTS (
        SELECT 1 FROM pg_type t
        JOIN pg_enum e ON e.enumtypid = t.oid
        WHERE t.typname = 'tokenauthmethod' AND e.enumlabel = 'NONE'
      ) THEN
        ALTER TYPE tokenauthmethod RENAME VALUE 'NONE' TO 'none';
      END IF;

      IF EXISTS (
        SELECT 1 FROM pg_type t
        JOIN pg_enum e ON e.enumtypid = t.oid
        WHERE t.typname = 'tokenauthmethod' AND e.enumlabel = 'CLIENT_SECRET_POST'
      ) THEN
        ALTER TYPE tokenauthmethod RENAME VALUE 'CLIENT_SECRET_POST' TO 'client_secret_post';
      END IF;

      IF EXISTS (
        SELECT 1 FROM pg_type t
        JOIN pg_enum e ON e.enumtypid = t.oid
        WHERE t.typname = 'tokenauthmethod' AND e.enumlabel = 'CLIENT_SECRET_BASIC'
      ) THEN
        ALTER TYPE tokenauthmethod RENAME VALUE 'CLIENT_SECRET_BASIC' TO 'client_secret_basic';
      END IF;
    END$$;
    """)

    # вернуть дефолты в нижнем регистре
    op.alter_column("clients", "type", server_default=sa.text("'public'::clienttype"))
    op.alter_column(
        "clients",
        "token_endpoint_auth_method",
        server_default=sa.text("'none'::tokenauthmethod"),
    )

def downgrade() -> None:
    op.alter_column("clients", "type", server_default=None)
    op.alter_column("clients", "token_endpoint_auth_method", server_default=None)

    op.execute("""
    DO $$
    BEGIN
      IF EXISTS (
        SELECT 1 FROM pg_type t
        JOIN pg_enum e ON e.enumtypid = t.oid
        WHERE t.typname = 'clienttype' AND e.enumlabel = 'public'
      ) THEN
        ALTER TYPE clienttype RENAME VALUE 'public' TO 'PUBLIC';
      END IF;

      IF EXISTS (
        SELECT 1 FROM pg_type t
        JOIN pg_enum e ON e.enumtypid = t.oid
        WHERE t.typname = 'clienttype' AND e.enumlabel = 'confidential'
      ) THEN
        ALTER TYPE clienttype RENAME VALUE 'confidential' TO 'CONFIDENTIAL';
      END IF;
    END$$;
    """)

    op.execute("""
    DO $$
    BEGIN
      IF EXISTS (
        SELECT 1 FROM pg_type t
        JOIN pg_enum e ON e.enumtypid = t.oid
        WHERE t.typname = 'tokenauthmethod' AND e.enumlabel = 'none'
      ) THEN
        ALTER TYPE tokenauthmethod RENAME VALUE 'none' TO 'NONE';
      END IF;

      IF EXISTS (
        SELECT 1 FROM pg_type t
        JOIN pg_enum e ON e.enumtypid = t.oid
        WHERE t.typname = 'tokenauthmethod' AND e.enumlabel = 'client_secret_post'
      ) THEN
        ALTER TYPE tokenauthmethod RENAME VALUE 'client_secret_post' TO 'CLIENT_SECRET_POST';
      END IF;

      IF EXISTS (
        SELECT 1 FROM pg_type t
        JOIN pg_enum e ON e.enumtypid = t.oid
        WHERE t.typname = 'tokenauthmethod' AND e.enumlabel = 'client_secret_basic'
      ) THEN
        ALTER TYPE tokenauthmethod RENAME VALUE 'client_secret_basic' TO 'CLIENT_SECRET_BASIC';
      END IF;
    END$$;
    """)

    op.alter_column("clients", "type", server_default=sa.text("'PUBLIC'::clienttype"))
    op.alter_column(
        "clients",
        "token_endpoint_auth_method",
        server_default=sa.text("'NONE'::tokenauthmethod"),
    )
