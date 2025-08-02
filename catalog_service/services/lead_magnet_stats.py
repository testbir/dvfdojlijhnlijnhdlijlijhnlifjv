# catalog_service/services/lead_magnet_stats.py

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from catalog_service.models.lead_magnet import LeadMagnet


async def fetch_user_course_ids(user_id: int, client: AsyncClient) -> list[int]:
    # Можно подстроить под конкретный путь вашего `admin_service` или `auth_service`
    resp = await client.get(f"http://adminservice/internal/users/{user_id}/courses")
    resp.raise_for_status()
    return resp.json()  # ожидается список ID курсов


async def calculate_lead_magnet_stats(
    lead_magnet_id: int,
    session: AsyncSession,
    client: AsyncClient,
) -> dict:
    # Получаем связку
    result = await session.execute(select(LeadMagnet).where(LeadMagnet.id == lead_magnet_id))
    lead_magnet = result.scalar_one_or_none()
    if not lead_magnet:
        raise ValueError("Связка не найдена")

    lead_course_id = lead_magnet.lead_course_id
    upsell_course_id = lead_magnet.upsell_course_id

    # Получаем пользователей, купивших лид-курс
    resp = await client.get(f"http://adminservice/internal/analytics/users-with-course/{lead_course_id}")
    resp.raise_for_status()
    user_ids = resp.json()  # список user_id

    total_leads = len(user_ids)
    bought_upsell = 0

    for user_id in user_ids:
        try:
            course_ids = await fetch_user_course_ids(user_id, client)
            if upsell_course_id in course_ids:
                bought_upsell += 1
        except Exception:
            continue  # пропускаем ошибки по пользователю

    conversion = round(bought_upsell / total_leads, 2) if total_leads > 0 else 0.0

    return {
        "total_leads": total_leads,
        "viewed_upsell_page": None,  # пока не реализовано
        "bought_upsell": bought_upsell,
        "conversion": conversion,
    }
