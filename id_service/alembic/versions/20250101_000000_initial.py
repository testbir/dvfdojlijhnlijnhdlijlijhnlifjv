# id_service/alembic/versions/20250101_000000_initial.py

"""initial

Revision ID: 0001_initial
Revises:
Create Date: 2025-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as psql

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- ENUM types: создаём один раз вручную и переиспользуем ---
    client_type = psql.ENUM("PUBLIC", "CONFIDENTIAL", name="clienttype", create_type=False)
    
    token_auth_method = psql.ENUM("NONE", "CLIENT_SECRET_POST", "CLIENT_SECRET_BASIC", name="tokenauthmethod", create_type=False)
    
    email_code_purpose = psql.ENUM(
        "register", "reset", "change_email",
        name="emailcodepurpose",
        create_type=False,
    )

    bind = op.get_bind()
    client_type.create(bind, checkfirst=True)
    token_auth_method.create(bind, checkfirst=True)
    email_code_purpose.create(bind, checkfirst=True)

    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_password_change_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ux_users_email_lower", "users", [sa.text("lower(email)")], unique=True)
    op.create_index("ux_users_username", "users", ["username"], unique=True)

    # --- clients ---
    op.create_table(
        "clients",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("client_id", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", client_type, nullable=False, server_default=sa.text("'PUBLIC'::clienttype")),
        sa.Column("token_endpoint_auth_method", token_auth_method, nullable=False, server_default=sa.text("'NONE'::tokenauthmethod")),
        sa.Column("pkce_required", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("redirect_uris", psql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("post_logout_redirect_uris", psql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("backchannel_logout_uri", sa.Text(), nullable=True),
        sa.Column("frontchannel_logout_uri", sa.Text(), nullable=True),
        sa.Column("scopes", psql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[\"openid\",\"email\",\"profile\"]'::jsonb")),
        sa.Column("client_secret_hash", sa.Text(), nullable=True),
        sa.Column("secret_rotated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("client_id", name="ux_clients_client_id"),
    )

    # --- jwk_keys ---
    op.create_table(
        "jwk_keys",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("kid", sa.String(length=255), nullable=False),
        sa.Column("alg", sa.String(length=10), nullable=False, server_default="RS256"),
        sa.Column("public_pem", sa.Text(), nullable=False),
        sa.Column("private_pem_encrypted", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("rotated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_jwk_keys_active_kid", "jwk_keys", ["active", "kid"])
    op.create_index(op.f("ix_jwk_keys_kid"), "jwk_keys", ["kid"], unique=True)

    # --- auth_codes ---
    op.create_table(
        "auth_codes",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("code_hash", sa.String(length=255), nullable=False),
        sa.Column("client_id", sa.String(length=255), sa.ForeignKey("clients.client_id"), nullable=False),
        sa.Column("user_id", psql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("redirect_uri", sa.Text(), nullable=False),
        sa.Column("scope", sa.String(length=500), nullable=False),
        sa.Column("code_challenge_hash", sa.String(length=255), nullable=True),
        sa.Column("nonce", sa.String(length=255), nullable=True),
        sa.Column("state", sa.String(length=500), nullable=True),
        sa.Column("auth_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.UniqueConstraint("code_hash"),
    )
    op.create_index(op.f("ix_auth_codes_code_hash"), "auth_codes", ["code_hash"])
    op.create_index(op.f("ix_auth_codes_expires_at"), "auth_codes", ["expires_at"])

    # --- email_codes ---
    op.create_table(
        "email_codes",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", psql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("purpose", email_code_purpose, nullable=False),
        sa.Column("code_hash", sa.String(length=255), nullable=False),
        sa.Column("new_email", sa.String(length=255), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("resend_after", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
    )
    op.create_index("ix_email_codes_user_purpose", "email_codes", ["user_id", "purpose", "expires_at"])

    # --- refresh_tokens ---
    op.create_table(
        "refresh_tokens",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("jti", sa.String(length=255), nullable=False),
        sa.Column("user_id", psql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("client_id", sa.String(length=255), sa.ForeignKey("clients.client_id"), nullable=False),
        sa.Column("parent_jti", sa.String(length=255), nullable=True),
        sa.Column("prev_jti", sa.String(length=255), nullable=True),
        sa.Column("scope", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("rotated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_reason", sa.String(length=255), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.UniqueConstraint("jti"),
    )
    op.create_index("ix_refresh_tokens_user_client", "refresh_tokens", ["user_id", "client_id", "revoked_at", "expires_at"])
    op.create_index(op.f("ix_refresh_tokens_parent_jti"), "refresh_tokens", ["parent_jti"])
    op.create_index(op.f("ix_refresh_tokens_expires_at"), "refresh_tokens", ["expires_at"])
    op.create_index(op.f("ix_refresh_tokens_jti"), "refresh_tokens", ["jti"], unique=True)

    # --- idp_sessions ---
    op.create_table(
        "idp_sessions",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("session_id", sa.String(length=255), nullable=False),
        sa.Column("user_id", psql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("idle_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("max_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("session_id"),
    )
    op.create_index("ix_idp_sessions_user_revoked", "idp_sessions", ["user_id", "revoked_at"])
    op.create_index(op.f("ix_idp_sessions_idle_expires_at"), "idp_sessions", ["idle_expires_at"])
    op.create_index(op.f("ix_idp_sessions_max_expires_at"), "idp_sessions", ["max_expires_at"])
    op.create_index(op.f("ix_idp_sessions_session_id"), "idp_sessions", ["session_id"], unique=True)


def downgrade() -> None:
    op.drop_table("idp_sessions")
    op.drop_table("refresh_tokens")
    op.drop_table("email_codes")
    op.drop_table("auth_codes")
    op.drop_index("ix_jwk_keys_active_kid", table_name="jwk_keys")
    op.drop_index(op.f("ix_jwk_keys_kid"), table_name="jwk_keys")
    op.drop_table("jwk_keys")
    op.drop_table("clients")
    op.drop_index("ux_users_email_lower", table_name="users")
    op.drop_index("ux_users_username", table_name="users")
    op.drop_table("users")

    # enums (дропаем в конце)
    bind = op.get_bind()
    psql.ENUM(name="emailcodepurpose").drop(bind, checkfirst=True)
    psql.ENUM(name="tokenauthmethod").drop(bind, checkfirst=True)
    psql.ENUM(name="clienttype").drop(bind, checkfirst=True)
