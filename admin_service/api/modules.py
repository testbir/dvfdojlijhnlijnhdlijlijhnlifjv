# admin_service/api/modules.py

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Optional, List
import httpx
from core.config import settings
from utils.auth import get_current_admin_user
from models.admin import AdminUser
import logging

router = APIRouter(tags=["Admin - Modules"])
logger = logging.getLogger(__name__)

LEARNING_SERVICE_URL = settings.LEARNING_SERVICE_URL

def _hdr():
    return {"Authorization": f"Bearer {settings.INTERNAL_TOKEN}"}

@router.get("/admin/courses/{course_id}/modules/")
async def get_course_modules(
    course_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Получить все модули курса"""
    logger.info(f"Admin {current_admin.username} fetching modules for course {course_id}")
    
    async with httpx.AsyncClient(base_url=LEARNING_SERVICE_URL, timeout=15.0) as client:
        response = await client.get(
            f"/v1/admin/courses/{course_id}/modules/",
            headers=_hdr()
        )
        response.raise_for_status()
        return response.json()

@router.post("/admin/courses/{course_id}/modules/")
async def create_module(
    course_id: int,
    title: str = Body(...),
    group_title: Optional[str] = Body(None),
    order: Optional[int] = Body(None),
    sp_award: Optional[int] = Body(0),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Создать новый модуль в курсе"""
    logger.info(f"Admin {current_admin.username} creating module in course {course_id}")
    
    payload = {
        "title": title,
        "group_title": group_title,
        "order": order,
        "sp_award": sp_award
    }
    
    async with httpx.AsyncClient(base_url=LEARNING_SERVICE_URL, timeout=15.0) as client:
        response = await client.post(
            f"/v1/admin/courses/{course_id}/modules/",
            headers=_hdr(),
            json=payload
        )
        response.raise_for_status()
        return response.json()

@router.get("/admin/modules/{module_id}")
async def get_module(
    module_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Получить информацию о модуле"""
    logger.info(f"Admin {current_admin.username} fetching module {module_id}")
    
    async with httpx.AsyncClient(base_url=LEARNING_SERVICE_URL, timeout=15.0) as client:
        response = await client.get(
            f"/v1/admin/modules/{module_id}",
            headers=_hdr()
        )
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Модуль не найден")
        response.raise_for_status()
        return response.json()

@router.put("/admin/modules/{module_id}")
async def update_module(
    module_id: int,
    title: Optional[str] = Body(None),
    group_title: Optional[str] = Body(None),
    order: Optional[int] = Body(None),
    sp_award: Optional[int] = Body(None),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Обновить модуль"""
    logger.info(f"Admin {current_admin.username} updating module {module_id}")
    
    payload = {}
    if title is not None:
        payload["title"] = title
    if group_title is not None:
        payload["group_title"] = group_title
    if order is not None:
        payload["order"] = order
    if sp_award is not None:
        payload["sp_award"] = sp_award
    
    async with httpx.AsyncClient(base_url=LEARNING_SERVICE_URL, timeout=15.0) as client:
        response = await client.put(
            f"/v1/admin/modules/{module_id}",
            headers=_hdr(),
            json=payload
        )
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Модуль не найден")
        response.raise_for_status()
        return response.json()

@router.delete("/admin/modules/{module_id}")
async def delete_module(
    module_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Удалить модуль"""
    logger.warning(f"Admin {current_admin.username} deleting module {module_id}")
    
    async with httpx.AsyncClient(base_url=LEARNING_SERVICE_URL, timeout=15.0) as client:
        response = await client.delete(
            f"/v1/admin/modules/{module_id}",
            headers=_hdr()
        )
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Модуль не найден")
        response.raise_for_status()
        return {"success": True, "message": "Модуль удален"}

# =======================
# admin_service/api/blocks.py
# =======================

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Optional, List
import httpx
from core.config import settings
from utils.auth import get_current_admin_user
from models.admin import AdminUser
import logging

router = APIRouter(tags=["Admin - Blocks"])
logger = logging.getLogger(__name__)

LEARNING_SERVICE_URL = settings.LEARNING_SERVICE_URL

def _hdr():
    return {"Authorization": f"Bearer {settings.INTERNAL_TOKEN}"}

@router.get("/admin/modules/{module_id}/blocks/")
async def get_module_blocks(
    module_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Получить все блоки модуля"""
    logger.info(f"Admin {current_admin.username} fetching blocks for module {module_id}")
    
    async with httpx.AsyncClient(base_url=LEARNING_SERVICE_URL, timeout=15.0) as client:
        response = await client.get(
            f"/v1/admin/modules/{module_id}/blocks/",
            headers=_hdr()
        )
        response.raise_for_status()
        return response.json()

@router.post("/admin/modules/{module_id}/blocks/")
async def create_block(
    module_id: int,
    type: str = Body(...),  # text, video, code, image
    title: str = Body(...),
    content: str = Body(...),
    order: Optional[int] = Body(None),
    language: Optional[str] = Body(None),  # для блоков кода
    video_preview: Optional[str] = Body(None),  # для видео
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Создать новый блок в модуле"""
    logger.info(f"Admin {current_admin.username} creating block in module {module_id}")
    
    payload = {
        "type": type,
        "title": title,
        "content": content,
        "order": order,
        "language": language,
        "video_preview": video_preview
    }
    
    async with httpx.AsyncClient(base_url=LEARNING_SERVICE_URL, timeout=15.0) as client:
        response = await client.post(
            f"/v1/admin/modules/{module_id}/blocks/",
            headers=_hdr(),
            json=payload
        )
        response.raise_for_status()
        return response.json()

@router.get("/admin/blocks/{block_id}")
async def get_block(
    block_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Получить информацию о блоке"""
    logger.info(f"Admin {current_admin.username} fetching block {block_id}")
    
    async with httpx.AsyncClient(base_url=LEARNING_SERVICE_URL, timeout=15.0) as client:
        response = await client.get(
            f"/v1/admin/blocks/{block_id}",
            headers=_hdr()
        )
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Блок не найден")
        response.raise_for_status()
        return response.json()

@router.put("/admin/blocks/{block_id}")
async def update_block(
    block_id: int,
    type: Optional[str] = Body(None),
    title: Optional[str] = Body(None),
    content: Optional[str] = Body(None),
    order: Optional[int] = Body(None),
    language: Optional[str] = Body(None),
    video_preview: Optional[str] = Body(None),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Обновить блок"""
    logger.info(f"Admin {current_admin.username} updating block {block_id}")
    
    payload = {}
    if type is not None:
        payload["type"] = type
    if title is not None:
        payload["title"] = title
    if content is not None:
        payload["content"] = content
    if order is not None:
        payload["order"] = order
    if language is not None:
        payload["language"] = language
    if video_preview is not None:
        payload["video_preview"] = video_preview
    
    async with httpx.AsyncClient(base_url=LEARNING_SERVICE_URL, timeout=15.0) as client:
        response = await client.put(
            f"/v1/admin/blocks/{block_id}",
            headers=_hdr(),
            json=payload
        )
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Блок не найден")
        response.raise_for_status()
        return response.json()

@router.delete("/admin/blocks/{block_id}")
async def delete_block(
    block_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Удалить блок"""
    logger.warning(f"Admin {current_admin.username} deleting block {block_id}")
    
    async with httpx.AsyncClient(base_url=LEARNING_SERVICE_URL, timeout=15.0) as client:
        response = await client.delete(
            f"/v1/admin/blocks/{block_id}",
            headers=_hdr()
        )
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Блок не найден")
        response.raise_for_status()
        return {"success": True, "message": "Блок удален"}

@router.post("/admin/blocks/reorder/")
async def reorder_blocks(
    module_id: int = Body(...),
    blocks_order: List[dict] = Body(...),  # [{"id": block_id, "order": new_order}]
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Изменить порядок блоков в модуле"""
    logger.info(f"Admin {current_admin.username} reordering blocks in module {module_id}")
    
    async with httpx.AsyncClient(base_url=LEARNING_SERVICE_URL, timeout=15.0) as client:
        # Обновляем порядок для каждого блока
        for block_info in blocks_order:
            response = await client.put(
                f"/v1/admin/blocks/{block_info['id']}",
                headers=_hdr(),
                json={"order": block_info['order']}
            )
            response.raise_for_status()
        
        return {"success": True, "message": "Порядок блоков обновлен"}