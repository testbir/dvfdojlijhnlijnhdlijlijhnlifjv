# catalog_service/api/admin/lead_magnets.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from catalog_service.db.dependencies import get_db_session
from catalog_service.models.lead_magnet import LeadMagnet
from catalog_service.models.course import Course
from catalog_service.schemas.lead_magnet import LeadMagnetCreate, LeadMagnetRead

router = APIRouter(prefix="/lead-magnets")

@router.get("/", response_model=list[LeadMagnetRead])
async def list_lead_magnets(session: AsyncSession = Depends(get_db_session)):
    result = await session.execute(select(LeadMagnet))
    return result.scalars().all()

@router.post("/", response_model=LeadMagnetRead)
async def create_lead_magnet(
    data: LeadMagnetCreate,
    session: AsyncSession = Depends(get_db_session),
):
    # Проверка на одинаковые ID
    if data.lead_course_id == data.upsell_course_id:
        raise HTTPException(status_code=400, detail="ID курсов не должны совпадать")

    # Проверка на существование курсов
    for course_id in [data.lead_course_id, data.upsell_course_id]:
        result = await session.execute(select(Course).where(Course.id == course_id))
        course = result.scalar_one_or_none()
        if not course:
            raise HTTPException(status_code=404, detail=f"Курс с ID {course_id} не найден")

    # Проверка на дубли
    duplicate_result = await session.execute(
        select(LeadMagnet).where(
            LeadMagnet.lead_course_id == data.lead_course_id,
            LeadMagnet.upsell_course_id == data.upsell_course_id,
        )
    )
    duplicate = duplicate_result.scalar_one_or_none()
    if duplicate:
        raise HTTPException(status_code=400, detail="Такая связка уже существует")

    obj = LeadMagnet(**data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj

@router.delete("/{lead_magnet_id}", status_code=204)
async def delete_lead_magnet(
    lead_magnet_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    result = await session.execute(select(LeadMagnet).where(LeadMagnet.id == lead_magnet_id))
    lead_magnet = result.scalar_one_or_none()
    if not lead_magnet:
        raise HTTPException(status_code=404, detail="Связка не найдена")

    await session.delete(lead_magnet)
    await session.commit()