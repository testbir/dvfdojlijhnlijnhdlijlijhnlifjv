# id_service/crud/user.py

from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_
from sqlalchemy.exc import IntegrityError

from models import User
from schemas.user import UserCreate, UserUpdate
from core.security import security

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from models import User
from core.security import security

import logging
logger = logging.getLogger(__name__)


class UserCRUD:
    """CRUD operations for User model"""
    
    async def create(
        self,
        session: AsyncSession,
        user_create: UserCreate
    ) -> Optional[User]:
        """Create new user"""
        try:
            # Hash password
            password_hash = security.hash_password(user_create.password)
            
            # Create user
            user = User(
                email=user_create.email.lower(),
                username=user_create.username,
                password_hash=password_hash,
                email_verified=user_create.email_verified,
                created_at=datetime.now(timezone.utc)
            )
            
            session.add(user)
            await session.flush()
            
            logger.info(f"Created user with ID {user.id}")
            return user
            
        except IntegrityError as e:
            logger.warning(f"Failed to create user: {e}")
            await session.rollback()
            return None
    
    async def get_by_id(
        self,
        session: AsyncSession,
        user_id: str
    ) -> Optional[User]:
        """Get user by ID"""
        result = await session.execute(
            select(User).where(
                and_(
                    User.id == user_id,
                    User.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(
        self,
        session: AsyncSession,
        email: str
    ) -> Optional[User]:
        """Get user by email (case-insensitive)"""
        result = await session.execute(
            select(User).where(
                and_(
                    func.lower(User.email) == email.lower(),
                    User.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_username(
        self,
        session: AsyncSession,
        username: str
    ) -> Optional[User]:
        """Get user by username"""
        result = await session.execute(
            select(User).where(
                and_(
                    User.username == username,
                    User.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_email_or_username(
        self,
        session: AsyncSession,
        identifier: str
    ) -> Optional[User]:
        """Get user by email or username"""
        result = await session.execute(
            select(User).where(
                and_(
                    or_(
                        func.lower(User.email) == identifier.lower(),
                        User.username == identifier
                    ),
                    User.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def update(
        self,
        session: AsyncSession,
        user: User,
        user_update: UserUpdate
    ) -> User:
        """Update user"""
        update_data = user_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == "email" and value:
                value = value.lower()
            setattr(user, field, value)
        
        user.updated_at = datetime.now(timezone.utc)
        await session.flush()
        
        logger.info(f"Updated user {user.id}")
        return user
    
    async def update_password(
        self,
        session: AsyncSession,
        user: User,
        new_password: str
    ) -> User:
        """Update user password"""
        user.password_hash = security.hash_password(new_password)
        user.last_password_change_at = datetime.now(timezone.utc)
        user.updated_at = datetime.now(timezone.utc)
        user.failed_login_attempts = 0  # Reset failed attempts
        
        await session.flush()
        
        logger.info(f"Updated password for user {user.id}")
        return user
    
    async def verify_email(
        self,
        session: AsyncSession,
        user: User
    ) -> User:
        """Mark user email as verified"""
        user.email_verified = True
        user.updated_at = datetime.now(timezone.utc)
        
        await session.flush()
        
        logger.info(f"Verified email for user {user.id}")
        return user
    
    async def update_login_info(
        self,
        session: AsyncSession,
        user: User,
        success: bool = True
    ) -> User:
        """Update login information"""
        now = datetime.now(timezone.utc)
        
        if success:
            user.last_login_at = now
            user.failed_login_attempts = 0
        else:
            user.failed_login_attempts += 1
        
        user.updated_at = now
        await session.flush()
        
        return user
    
    async def soft_delete(
        self,
        session: AsyncSession,
        user: User
    ) -> User:
        """Soft delete user"""
        now = datetime.now(timezone.utc)
        user.deleted_at = now
        user.updated_at = now
        
        # Anonymize personal data
        user.email = f"deleted_{user.id}@deleted.local"
        user.username = f"deleted_{user.id}"
        
        await session.flush()
        
        logger.info(f"Soft deleted user {user.id}")
        return user
    
    async def check_email_exists(
        self,
        session: AsyncSession,
        email: str,
        exclude_user_id: Optional[str] = None
    ) -> bool:
        """Check if email already exists"""
        query = select(User).where(
            and_(
                func.lower(User.email) == email.lower(),
                User.deleted_at.is_(None)
            )
        )
        
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)
        
        result = await session.execute(query.exists().select())
        return result.scalar()
    
    async def check_username_exists(
        self,
        session: AsyncSession,
        username: str,
        exclude_user_id: Optional[str] = None
    ) -> bool:
        """Check if username already exists"""
        query = select(User).where(
            and_(
                User.username == username,
                User.deleted_at.is_(None)
            )
        )
        
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)
        
        result = await session.execute(query.exists().select())
        return result.scalar()
    
    async def rehash_password(
        self,
        session: AsyncSession,
        user: User,
        raw_password: str
    ) -> User:
        """
        Тихий ре-хэш пароля (без пометки last_password_change_at).
        Меняет только password_hash/updated_at/failed_login_attempts.
        """
        user.password_hash = security.hash_password(raw_password)
        user.updated_at = datetime.now(timezone.utc)
        user.failed_login_attempts = 0
        await session.flush()
        return user


user_crud = UserCRUD()