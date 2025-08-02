# admin_service/services/catalog_api.py

import httpx
from schemas import CourseCreate
from schemas import CourseCreate, ModuleCreate, ContentBlockCreate
from fastapi.encoders import jsonable_encoder



from core.config import settings

CATALOG_SERVICE_URL = settings.CATALOG_SERVICE_URL



async def get_courses():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CATALOG_SERVICE_URL}/courses/")
        response.raise_for_status()
        return response.json()


async def create_course(data: CourseCreate):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{CATALOG_SERVICE_URL}/courses/internal/courses/",
            json=jsonable_encoder(data) 
        )
        response.raise_for_status()
        return response.json()




async def get_course(course_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CATALOG_SERVICE_URL}/courses/{course_id}/")
        response.raise_for_status()
        return response.json()


async def update_course(course_id: int, data: CourseCreate):
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{CATALOG_SERVICE_URL}/courses/internal/courses/{course_id}",
            json=jsonable_encoder(data)  
        )
        response.raise_for_status()
        return response.json()



async def delete_course(course_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{CATALOG_SERVICE_URL}/courses/internal/courses/{course_id}")
        response.raise_for_status()
        return response.json()



# Получение модуля
async def get_module(module_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CATALOG_SERVICE_URL}/courses/internal/modules/{module_id}")
        response.raise_for_status()
        return response.json()

# Обновление модуля
async def update_module(module_id: int, data: ModuleCreate):
    async with httpx.AsyncClient() as client:
        response = await client.put(f"{CATALOG_SERVICE_URL}/courses/internal/modules/{module_id}", json=data.dict())
        response.raise_for_status()
        return response.json()

# Удаление модуля
async def delete_module(module_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{CATALOG_SERVICE_URL}/courses/internal/modules/{module_id}")
        response.raise_for_status()
        return response.json()



# Получение контент-блока
async def get_block(block_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CATALOG_SERVICE_URL}/courses/internal/blocks/{block_id}")
        response.raise_for_status()
        return response.json()


# Обновление контент-блока
async def update_block(block_id: int, data: ContentBlockCreate):
    async with httpx.AsyncClient() as client:
        response = await client.put(f"{CATALOG_SERVICE_URL}/courses/internal/blocks/{block_id}", json=data.dict())
        response.raise_for_status()
        return response.json()



# Получение списка модулей для курса
async def get_modules_for_course(course_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CATALOG_SERVICE_URL}/courses/{course_id}/modules/")
        response.raise_for_status()
        return response.json()




# Получение списка блоков для модуля
async def get_blocks_for_module(module_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CATALOG_SERVICE_URL}/courses/internal/modules/{module_id}/blocks/")
        response.raise_for_status()
        return response.json()



# Удаление контент-блока
async def delete_block(block_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{CATALOG_SERVICE_URL}/courses/internal/blocks/{block_id}")
        response.raise_for_status()
        return response.json()



# Обновление порядка блоков
async def update_blocks_order(module_id: int, blocks: list[dict]):
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{CATALOG_SERVICE_URL}/courses/internal/modules/{module_id}/courses/blocks/order/",
            json=blocks
        )
        response.raise_for_status()
        return response.json()


# --- BANNERS ---
async def get_banners():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CATALOG_SERVICE_URL}/internal/banners/")
        response.raise_for_status()
        return response.json()

async def create_banner(data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{CATALOG_SERVICE_URL}/internal/banners/", json=data)
        response.raise_for_status()
        return response.json()

async def delete_banner(banner_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{CATALOG_SERVICE_URL}/internal/banners/{banner_id}")
        response.raise_for_status()
        return response.json()


# --- PROMOS ---
async def get_promos():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CATALOG_SERVICE_URL}/promos/internal/promos/")
        response.raise_for_status()
        return response.json()

async def create_promo(data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{CATALOG_SERVICE_URL}/promos/internal/promos/", json=data)
        response.raise_for_status()
        return response.json()

async def delete_promo(promo_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{CATALOG_SERVICE_URL}/promos/internal/promos/{promo_id}")
        response.raise_for_status()
        return response.json()


async def update_banner(banner_id: int, data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.put(f"{CATALOG_SERVICE_URL}/internal/banners/{banner_id}", json=data)
        response.raise_for_status()
        return response.json()



async def get_course_internal(course_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CATALOG_SERVICE_URL}/courses/internal/courses/{course_id}")
        response.raise_for_status()
        return response.json()
