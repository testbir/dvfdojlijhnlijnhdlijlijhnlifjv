# catalog_service/utils/auth_client.py

import httpx
from fastapi import HTTPException
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# URL auth_service (в Docker контейнере)
AUTH_SERVICE_URL = "http://authservice:8000"

async def get_user_data_from_auth(user_id: int, access_token: str) -> Dict[str, Any]:
    """
    Получает данные пользователя из auth_service
    
    Args:
        user_id: ID пользователя 
        access_token: JWT токен для авторизации
        
    Returns:
        Dict с данными пользователя (id, username, email)
        
    Raises:
        HTTPException: При ошибке запроса к auth_service
    """
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/api/user/",
                headers=headers
            )
            
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"Получены данные пользователя {user_id} из auth_service")
                return user_data
            elif response.status_code == 401:
                logger.warning(f"Неавторизованный запрос для пользователя {user_id}")
                raise HTTPException(
                    status_code=401, 
                    detail="Не авторизован"
                )
            else:
                logger.error(f"Ошибка auth_service: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=500,
                    detail="Ошибка получения данных пользователя"
                )
                
    except httpx.TimeoutException:
        logger.error(f"Таймаут при запросе к auth_service для пользователя {user_id}")
        raise HTTPException(
            status_code=500,
            detail="Сервис авторизации недоступен"
        )
    except httpx.RequestError as e:
        logger.error(f"Ошибка соединения с auth_service: {e}")
        raise HTTPException(
            status_code=500,
            detail="Ошибка соединения с сервисом авторизации"
        )