#admin_service/api/auth.py


from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from admin_service.db import SessionLocal
from admin_service.models.admin import AdminUser
from admin_service.utils.security import verify_password, create_access_token
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(data: LoginRequest):
    db = SessionLocal()
    try:
        user = db.query(AdminUser).filter(AdminUser.username == data.username).first()
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
        token = create_access_token({"sub": str(user.id)}, expires_delta=timedelta(hours=12))
        return {"access_token": token, "token_type": "bearer"}
    finally:
        db.close()
