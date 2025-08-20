# id_service/db/init_db.py

import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.config import settings
from core.security import security
from models import Client, ClientType, User


logger = logging.getLogger(__name__)


async def init_db(session: AsyncSession) -> None:
    """Seed только для dev. В проде — миграции Alembic и никакого create_all."""
    if settings.APP_ENV != "development":
        return

    result = await session.execute(select(Client).limit(1))
    if result.scalar_one_or_none():
        logger.info("Database already initialized")
        return

    logger.info("Creating initial data for development...")
    
    # Create local development clients
    clients_data = [
        {
            "client_id": settings.TEACH_CLIENT_ID,
            "name": "Teach Service (Local)",
            "type": ClientType.PUBLIC,
            "redirect_uris": [
                "http://localhost:3001/callback",
                "http://teach.localhost:3001/callback"
            ],
            "post_logout_redirect_uris": [
                "http://localhost:3001",
                "http://teach.localhost:3001"
            ],
            "backchannel_logout_uri": "http://localhost:3001/backchannel-logout",
            "scopes": ["openid", "email", "profile", "offline_access"]
        },
        {
            "client_id": settings.RUN_CLIENT_ID,
            "name": "Run Service (Local)",
            "type": ClientType.PUBLIC,
            "redirect_uris": [
                "http://localhost:3002/callback",
                "http://run.localhost:3002/callback"
            ],
            "post_logout_redirect_uris": [
                "http://localhost:3002",
                "http://run.localhost:3002"
            ],
            "backchannel_logout_uri": "http://localhost:3002/backchannel-logout",
            "scopes": ["openid", "email", "profile", "offline_access"]
        },
        {
            "client_id": settings.LEARN_CLIENT_ID,
            "name": "Learn Service (Local)",
            "type": ClientType.PUBLIC,
            "redirect_uris": [
                "http://localhost:3003/callback",
                "http://learn.localhost:3003/callback"
            ],
            "post_logout_redirect_uris": [
                "http://localhost:3003",
                "http://learn.localhost:3003"
            ],
            "backchannel_logout_uri": "http://localhost:3003/backchannel-logout",
            "scopes": ["openid", "email", "profile", "offline_access"]
        }
    ]
    
    for client_data in clients_data:
        session.add(Client(**client_data))
    
    test_user = User(
        email="test@asynq.ru",
        username="testuser",
        password_hash=security.hash_password("Test123!"),
        email_verified=True,
        created_at=datetime.now(timezone.utc)
    )
    session.add(test_user)

    await session.commit()
    logger.info("Dev data created")