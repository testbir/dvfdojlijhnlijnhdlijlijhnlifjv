# admin_service/api/lead_magnets.py

from fastapi import APIRouter
from schemas import LeadMagnetCreate, LeadMagnetRead, LeadMagnetStats
from services import catalog_api

router = APIRouter(prefix="/internal/lead-magnets", tags=["LeadMagnets"])


@router.get("/", response_model=list[LeadMagnetRead])
async def list_lead_magnets():
    return await catalog_api.get_lead_magnets()


@router.post("/", response_model=LeadMagnetRead)
async def create_lead_magnet(data: LeadMagnetCreate):
    return await catalog_api.create_lead_magnet(data.dict())


@router.delete("/{lead_magnet_id}", status_code=204)
async def delete_lead_magnet(lead_magnet_id: int):
    await catalog_api.delete_lead_magnet(lead_magnet_id)


@router.get("/{lead_magnet_id}/stats", response_model=LeadMagnetStats)
async def get_lead_magnet_stats(lead_magnet_id: int):
    return await catalog_api.get_lead_magnet_stats(lead_magnet_id)
