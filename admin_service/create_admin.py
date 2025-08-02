#!/usr/bin/env python3

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from core.config import settings
from models.admin import AdminUser
from utils.security import get_password_hash

def create_admin():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    username = input("Введите логин админа: ")
    password = input("Введите пароль админа: ")
    
    # Проверяем, не существует ли уже
    existing = db.query(AdminUser).filter(AdminUser.username == username).first()
    if existing:
        print(f"Админ {username} уже существует!")
        return
    
    # Создаем админа
    admin = AdminUser(
        username=username,
        hashed_password=get_password_hash(password)
    )
    
    db.add(admin)
    db.commit()
    print(f"✅ Админ {username} создан!")
    db.close()

if __name__ == "__main__":
    create_admin()