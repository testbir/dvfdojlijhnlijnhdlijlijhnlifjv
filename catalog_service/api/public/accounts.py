# catalog_service/api/public/accounts.py

from fastapi import APIRouter, HTTPException, Request

from utils.auth import get_current_user_id
from utils.auth_client import get_user_data_from_auth

router = APIRouter()




    

@router.get("/profile/", summary="Профиль пользователя")
async def get_user_profile(request: Request):
    """
    Возвращает данные пользователя из auth_service
    """
    user_id = get_current_user_id(request)
    
    # Получаем токен из заголовка Authorization
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Отсутствует токен авторизации"
        )
    
    access_token = auth_header.replace("Bearer ", "")
    
    # Запрашиваем данные пользователя из auth_service
    user_data = await get_user_data_from_auth(user_id, access_token)
    
    return user_data