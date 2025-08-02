# admin_service/utils/auth.py

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from core.config import settings
from sqlalchemy.orm import Session
from db import get_db
from models.admin import AdminUser
import logging
from datetime import datetime, timezone

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
logger = logging.getLogger(__name__)


def get_current_admin_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> AdminUser:
    """
    Проверяет, что токен валиден И пользователь является админом
    
    Args:
        token: JWT токен из заголовка Authorization
        db: Сессия базы данных
        
    Returns:
        AdminUser: Объект админа
        
    Raises:
        HTTPException: Если токен невалиден, пользователь не найден или не является админом
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Недостаточно прав доступа",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Декодируем JWT токен
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            logger.warning("JWT токен не содержит user_id (sub)")
            raise credentials_exception
            
        # Дополнительные проверки JWT payload
        token_type = payload.get("token_type", "access")
        if token_type != "access":
            logger.warning(f"Неверный тип токена: {token_type}")
            raise credentials_exception
            
        # Проверяем срок действия токена
        exp = payload.get("exp")
        if exp:
            token_exp = datetime.fromtimestamp(exp, tz=timezone.utc)
            if datetime.now(timezone.utc) > token_exp:
                logger.warning("JWT токен истек")
                raise credentials_exception
                
        # Логируем информацию о токене для отладки
        logger.debug(f"JWT payload: user_id={user_id}, exp={exp}, token_type={token_type}")
            
    except JWTError as e:
        logger.warning(f"Ошибка декодирования JWT: {str(e)}")
        raise credentials_exception
    
    try:
        # КРИТИЧНО: Проверяем, что пользователь существует в админской таблице
        admin_user = db.query(AdminUser).filter(AdminUser.id == int(user_id)).first()
        
        if admin_user is None:
            logger.warning(f"Админ пользователь не найден в БД: user_id={user_id}")
            raise HTTPException(
                status_code=403,
                detail="Пользователь не является администратором"
            )
            
        # ДОПОЛНИТЕЛЬНО: Проверяем активность админа (если есть такое поле)
        if hasattr(admin_user, 'is_active') and not admin_user.is_active:
            logger.warning(f"Админ аккаунт деактивирован: user_id={user_id}, username={admin_user.username}")
            raise HTTPException(
                status_code=403,
                detail="Админ-аккаунт деактивирован"
            )
            
        # Проверяем срок последней активности (если есть такое поле)
        if hasattr(admin_user, 'last_login_at'):
            admin_user.last_login_at = datetime.utcnow()
            db.commit()
            
        logger.info(f"Успешная авторизация админа: {admin_user.username} (ID: {admin_user.id})")
        return admin_user
        
    except ValueError as e:
        logger.error(f"Невалидный user_id в токене: {user_id}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Ошибка при получении админа из БД: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка авторизации"
        )


def check_admin_permissions(admin_user: AdminUser, required_permission: str = None) -> bool:
    """
    Проверяет специфические права админа (для будущего расширения)
    
    Args:
        admin_user: Объект админа
        required_permission: Требуемое разрешение (например, "manage_courses")
        
    Returns:
        bool: True если права достаточны
        
    Raises:
        HTTPException: Если прав недостаточно
    """
    # Пока все админы имеют все права
    # В будущем можно добавить систему ролей:
    
    # Пример будущей реализации:
    # if hasattr(admin_user, 'role'):
    #     if admin_user.role == "super_admin":
    #         return True
    #     elif admin_user.role == "content_manager" and required_permission in ["manage_courses", "manage_content"]:
    #         return True
    #     elif admin_user.role == "moderator" and required_permission in ["manage_users"]:
    #         return True
    #     else:
    #         raise HTTPException(
    #             status_code=403, 
    #             detail=f"Недостаточно прав для действия: {required_permission}"
    #         )
    
    logger.debug(f"Проверка прав админа {admin_user.username}: {required_permission or 'базовые права'}")
    return True


def create_admin_audit_log(admin_user: AdminUser, action: str, details: dict = None):
    """
    Создает запись аудита действий админа
    
    Args:
        admin_user: Объект админа
        action: Описание действия
        details: Дополнительные детали действия
    """
    try:
        # TODO: Реализовать логирование в отдельную таблицу или внешний сервис
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "admin_id": admin_user.id,
            "admin_username": admin_user.username,
            "action": action,
            "details": details or {}
        }
        
        # Пока просто логируем в файл
        logger.info(f"ADMIN_AUDIT: {log_entry}")
        
        # В будущем можно добавить:
        # - Запись в отдельную таблицу audit_logs
        # - Отправка в внешний сервис логирования
        # - Уведомления при критичных действиях
        
    except Exception as e:
        logger.error(f"Ошибка создания аудит-лога: {str(e)}")


# Декоратор для автоматического логирования действий
def audit_action(action_name: str):
    """
    Декоратор для автоматического аудита действий админа
    
    Args:
        action_name: Название действия для лога
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Ищем админа в аргументах
            admin_user = None
            for arg in kwargs.values():
                if isinstance(arg, AdminUser):
                    admin_user = arg
                    break
            
            if admin_user:
                create_admin_audit_log(admin_user, action_name, {
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": {k: str(v) for k, v in kwargs.items() if not isinstance(v, AdminUser)}
                })
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Функция для проверки безопасности пароля (если потребуется)
def validate_admin_password(password: str) -> bool:
    """
    Проверяет требования к паролю админа
    
    Args:
        password: Пароль для проверки
        
    Returns:
        bool: True если пароль соответствует требованиям
    """
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    return has_upper and has_lower and has_digit and has_special


# Функция для генерации безопасного пароля
def generate_admin_password(length: int = 12) -> str:
    """
    Генерирует безопасный пароль для админа
    
    Args:
        length: Длина пароля
        
    Returns:
        str: Сгенерированный пароль
    """
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    # Убеждаемся, что пароль соответствует требованиям
    if validate_admin_password(password):
        return password
    else:
        # Рекурсивно генерируем новый пароль
        return generate_admin_password(length)