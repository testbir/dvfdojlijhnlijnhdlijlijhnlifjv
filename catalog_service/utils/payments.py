# catalog_service/utils/payments.py

from typing import Optional
import logging

logger = logging.getLogger(__name__)

async def verify_payment(payment_id: str, expected_amount: float, course_id: int) -> bool:
    """
    Проверка платежа через платежную систему
    """
    # В разработке - принимаем тестовые ID
    if payment_id.startswith("test_"):
        logger.info(f"Тестовый платеж {payment_id} для курса {course_id}")
        return True
    
    # TODO: Когда подключите реальную платежную систему:
    # try:
    #     payment = await yookassa_client.get_payment(payment_id)
    #     return (payment.status == "succeeded" and 
    #             payment.amount.value == expected_amount)
    # except Exception as e:
    #     logger.error(f"Ошибка проверки платежа: {e}")
    #     return False
    
    # Пока что для продакшена возвращаем False (безопасно)
    logger.warning(f"Попытка оплаты без настроенной платежной системы: {payment_id}")
    return False

async def create_payment(course_id: int, amount: float, user_id: int) -> Optional[str]:
    """
    Создание платежа
    """
    # TODO: Интеграция с платежной системой
    # payment = await yookassa_client.create_payment({
    #     "amount": {"value": str(amount), "currency": "RUB"},
    #     "description": f"Курс {course_id}",
    #     "metadata": {"user_id": user_id, "course_id": course_id}
    # })
    # return payment.id
    
    return f"test_payment_{course_id}_{user_id}"