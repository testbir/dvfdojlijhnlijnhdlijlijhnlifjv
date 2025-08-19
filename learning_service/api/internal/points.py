# learning_service/api/internal/points.py
import httpx
from core.config import settings

async def award_points(user_id: int, amount: int, reason: str, idem_key: str, module_id: int | None = None) -> None:
    url = f"{settings.POINTS_SERVICE_URL}/v1/internal/points/award"
    headers = {"Authorization": f"Bearer {settings.INTERNAL_TOKEN}"}
    payload = {
        "user_id": user_id,
        "amount": amount,
        "reason": reason,
        "idempotency_key": idem_key,
        "source_service": "learning_service",
        "reference_type": "module",
        "reference_id": str(module_id) if module_id is not None else None,
    }
    async with httpx.AsyncClient(timeout=3.0) as client:
        r = await client.post(url, json=payload, headers=headers)
        r.raise_for_status()