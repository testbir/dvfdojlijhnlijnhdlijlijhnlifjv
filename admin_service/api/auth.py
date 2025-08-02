#admin_service/api/auth.py


from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from db import get_db
from models.admin import AdminUser
from schemas import AdminLogin, TokenResponse
from utils.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenResponse)
def login(
    data: AdminLogin = Body(...),  # Явно указываем Body
    db: Session = Depends(get_db)
):
    user = db.query(AdminUser).filter(AdminUser.username == data.username).first()
    if not user:
        print("❌ Пользователь не найден")
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    if not verify_password(data.password, user.hashed_password):
        print("❌ Неверный пароль")
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    token = create_access_token({"sub": str(user.id)})
    print("✅ Вход успешен, токен создан")

    return {"access_token": token, "token_type": "bearer"}
