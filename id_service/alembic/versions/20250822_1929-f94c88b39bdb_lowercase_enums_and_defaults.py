"""lowercase enums and defaults

Revision ID: f94c88b39bdb
Revises: 4844acc09d05
Create Date: 2025-08-22 19:29:09.507410

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f94c88b39bdb'
down_revision = '4844acc09d05'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Переименовать значения ENUM, если они ещё в верхнем регистре
    op.execute("""
    DO $$
    BEGIN
      IF EXISTS (
        SELECT 1 FROM pg_enum e JOIN pg_type t ON t.oid=e.enumtypid
        WHERE t.typname='clienttype' AND e.enumlabel='PUBLIC'
      ) THEN
        ALTER TYPE clienttype RENAME VALUE 'PUBLIC' TO 'public';
      END IF;

      IF EXISTS (
        SELECT 1 FROM pg_enum e JOIN pg_type t ON t.oid=e.enumtypid
        WHERE t.typname='clienttype' AND e.enumlabel='CONFIDENTIAL'
      ) THEN
        ALTER TYPE clienttype RENAME VALUE 'CONFIDENTIAL' TO 'confidential';
      END IF;

      IF EXISTS (
        SELECT 1 FROM pg_enum e JOIN pg_type t ON t.oid=e.enumtypid
        WHERE t.typname='tokenauthmethod' AND e.enumlabel='NONE'
      ) THEN
        ALTER TYPE tokenauthmethod RENAME VALUE 'NONE' TO 'none';
      END IF;

      IF EXISTS (
        SELECT 1 FROM pg_enum e JOIN pg_type t ON t.oid=e.enumtypid
        WHERE t.typname='tokenauthmethod' AND e.enumlabel='CLIENT_SECRET_POST'
      ) THEN
        ALTER TYPE tokenauthmethod RENAME VALUE 'CLIENT_SECRET_POST' TO 'client_secret_post';
      END IF;

      IF EXISTS (
        SELECT 1 FROM pg_enum e JOIN pg_type t ON t.oid=e.enumtypid
        WHERE t.typname='tokenauthmethod' AND e.enumlabel='CLIENT_SECRET_BASIC'
      ) THEN
        ALTER TYPE tokenauthmethod RENAME VALUE 'CLIENT_SECRET_BASIC' TO 'client_secret_basic';
      END IF;
    END $$;
    """)

    # Обновить дефолты в таблице clients
    op.execute("ALTER TABLE clients ALTER COLUMN type SET DEFAULT 'public'::clienttype")
    op.execute("""
        ALTER TABLE clients ALTER COLUMN token_endpoint_auth_method
        SET DEFAULT 'none'::tokenauthmethod
    """)


def downgrade() -> None:
    # Вернуть дефолты
    op.execute("""
        ALTER TABLE clients ALTER COLUMN token_endpoint_auth_method
        SET DEFAULT 'NONE'::tokenauthmethod
    """)
    op.execute("ALTER TABLE clients ALTER COLUMN type SET DEFAULT 'PUBLIC'::clienttype")

    # Вернуть значения ENUM в верхний регистр (если вдруг были понижены)
    op.execute("""
    DO $$
    BEGIN
      IF EXISTS (
        SELECT 1 FROM pg_enum e JOIN pg_type t ON t.oid=e.enumtypid
        WHERE t.typname='tokenauthmethod' AND e.enumlabel='client_secret_basic'
      ) THEN
        ALTER TYPE tokenauthmethod RENAME VALUE 'client_secret_basic' TO 'CLIENT_SECRET_BASIC';
      END IF;

      IF EXISTS (
        SELECT 1 FROM pg_enum e JOIN pg_type t ON t.oid=e.enumtypid
        WHERE t.typname='tokenauthmethod' AND e.enumlabel='client_secret_post'
      ) THEN
        ALTER TYPE tokenauthmethod RENAME VALUE 'client_secret_post' TO 'CLIENT_SECRET_POST';
      END IF;

      IF EXISTS (
        SELECT 1 FROM pg_enum e JOIN pg_type t ON t.oid=e.enumtypid
        WHERE t.typname='tokenauthmethod' AND e.enumlabel='none'
      ) THEN
        ALTER TYPE tokenauthmethod RENAME VALUE 'none' TO 'NONE';
      END IF;

      IF EXISTS (
        SELECT 1 FROM pg_enum e JOIN pg_type t ON t.oid=e.enumtypid
        WHERE t.typname='clienttype' AND e.enumlabel='confidential'
      ) THEN
        ALTER TYPE clienttype RENAME VALUE 'confidential' TO 'CONFIDENTIAL';
      END IF;

      IF EXISTS (
        SELECT 1 FROM pg_enum e JOIN pg_type t ON t.oid=e.enumtypid
        WHERE t.typname='clienttype' AND e.enumlabel='public'
      ) THEN
        ALTER TYPE clienttype RENAME VALUE 'public' TO 'PUBLIC';
      END IF;
    END $$;
    """)