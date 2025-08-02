# catalog_service/utils/cache.py

import redis
import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta
from functools import wraps
import hashlib
from core.config import settings

redis_client = redis.Redis(host='redis_cache', port=6379, db=0, decode_responses=True)

def cache_result(expire_time=300):  # 5 минут по умолчанию
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Создаем ключ кэша
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Проверяем кэш
            try:
                cached = redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            except:
                pass  # Если Redis недоступен, просто игнорируем кэш
            
            # Выполняем функцию
            result = await func(*args, **kwargs)
            
            # Сохраняем в кэш
            try:
                redis_client.setex(cache_key, expire_time, json.dumps(result, default=str))
            except:
                pass  # Если Redis недоступен, просто игнорируем
                
            return result
        return wrapper
    return decorator

# Подключение к Redis
try:
    redis_client = redis.Redis(
        host='redis',  # или ваш Redis хост
        port=6379,
        db=0,
        decode_responses=False,  # Для поддержки pickle
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )
    redis_client.ping()  # Проверяем соединение
    REDIS_AVAILABLE = True
except:
    REDIS_AVAILABLE = False
    redis_client = None

class CacheManager:
    """Менеджер кэширования для высоконагруженных операций"""
    
    @staticmethod
    def generate_key(*args, **kwargs) -> str:
        """Генерирует уникальный ключ для кэша"""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    @staticmethod
    def set(key: str, value: Any, ttl: int = 300) -> bool:
        """Сохраняет данные в кэш"""
        if not REDIS_AVAILABLE:
            return False
        
        try:
            serialized = pickle.dumps(value)
            return redis_client.setex(key, ttl, serialized)
        except Exception as e:
            print(f"Cache SET error: {e}")
            return False
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Получает данные из кэша"""
        if not REDIS_AVAILABLE:
            return None
        
        try:
            data = redis_client.get(key)
            if data:
                return pickle.loads(data)
            return None
        except Exception as e:
            print(f"Cache GET error: {e}")
            return None
    
    @staticmethod
    def delete(key: str) -> bool:
        """Удаляет данные из кэша"""
        if not REDIS_AVAILABLE:
            return False
        
        try:
            return bool(redis_client.delete(key))
        except Exception as e:
            print(f"Cache DELETE error: {e}")
            return False
    
    @staticmethod
    def delete_pattern(pattern: str) -> bool:
        """Удаляет все ключи по паттерну"""
        if not REDIS_AVAILABLE:
            return False
        
        try:
            keys = redis_client.keys(pattern)
            if keys:
                return bool(redis_client.delete(*keys))
            return True
        except Exception as e:
            print(f"Cache DELETE_PATTERN error: {e}")
            return False

def cache_result(ttl: int = 300, key_prefix: str = ""):
    """
    Декоратор для кэширования результатов функций
    
    Args:
        ttl: время жизни кэша в секундах
        key_prefix: префикс для ключа кэша
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Генерируем ключ кэша
            cache_key = f"{key_prefix}:{func.__name__}:{CacheManager.generate_key(*args, **kwargs)}"
            
            # Пытаемся получить из кэша
            cached_result = CacheManager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Выполняем функцию и сохраняем результат
            result = await func(*args, **kwargs)
            CacheManager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Специальные функции для курсов

def cache_course_structure(course_id: int, data: Any, ttl: int = 600):
    """Кэширует структуру курса на 10 минут"""
    key = f"course_structure:{course_id}"
    CacheManager.set(key, data, ttl)

def get_cached_course_structure(course_id: int) -> Optional[Any]:
    """Получает структуру курса из кэша"""
    key = f"course_structure:{course_id}"
    return CacheManager.get(key)

def invalidate_course_cache(course_id: int):
    """Инвалидирует весь кэш курса"""
    pattern = f"course_*:{course_id}*"
    CacheManager.delete_pattern(pattern)

def cache_user_progress(user_id: int, course_id: int, data: Any, ttl: int = 180):
    """Кэширует прогресс пользователя на 3 минуты"""
    key = f"user_progress:{user_id}:{course_id}"
    CacheManager.set(key, data, ttl)

def get_cached_user_progress(user_id: int, course_id: int) -> Optional[Any]:
    """Получает прогресс пользователя из кэша"""
    key = f"user_progress:{user_id}:{course_id}"
    return CacheManager.get(key)

def invalidate_user_progress_cache(user_id: int, course_id: int):
    """Инвалидирует кэш прогресса пользователя"""
    key = f"user_progress:{user_id}:{course_id}"
    CacheManager.delete(key)

# Пример использования:
# @cache_result(ttl=600, key_prefix="course_learning")
# async def get_course_learning_data(course_id: int, user_id: int):
#     # Ваша логика
#     pass