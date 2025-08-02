#admin_service/utils/auth.py


from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from core.config import settings
from sqlalchemy.orm import Session
from db import get_db
from models.admin import AdminUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_admin_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> AdminUser:
    """
    Проверяет, что токен валиден И пользователь является админом
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Недостаточно прав доступа",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # ВАЖНО: Проверяем, что пользователь существует в админской таблице
    admin_user = db.query(AdminUser).filter(AdminUser.id == int(user_id)).first()
    if admin_user is None:
        raise credentials_exception
        
    return admin_user
