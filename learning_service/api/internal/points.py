# learning_service/api/internal/points.py
import httpx
from core.config import settings

async def award_points(user_id: int, amount: int, reason: str, idem_key: str) -> None:
    url = f"{settings.POINTS_SERVICE_URL}/v1/internal/points/award"
    headers = {
        "Authorization": f"Bearer {settings.INTERNAL_TOKEN}",
        "Idempotency-Key": idem_key,
    }
    async with httpx.AsyncClient(timeout=3.0) as client:
        r = await client.post(url, json={"user_id": user_id, "amount": amount, "reason": reason}, headers=headers)
        r.raise_for_status()
