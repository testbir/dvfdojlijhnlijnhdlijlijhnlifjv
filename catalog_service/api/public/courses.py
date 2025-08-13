

























@router.get("/", response_model=List[CourseListSchema], summary="Список всех курсов")
@cache_result(ttl=600)
async def list_courses(request: Request, db: AsyncSession = Depends(get_db_session)):
    user_id = None
    try:
        user_id = get_current_user_id(request)  # Пробуем получить ID пользователя, если авторизован
    except:
        pass  # Если не авторизован — просто без доступа к платным курсам

    result = await db.execute(select(Course).order_by(Course.order.asc()))
    courses = result.scalars().all()
    result_list = []

    for course in courses:
        is_discount_active, _ = get_discount_info(course)  # Проверяем активность скидки

        # Расчёт финальной цены с учётом скидки (если она активна)
        if is_discount_active:
            final_price = float(course.price or 0.0) * (1 - float(course.discount or 0) / 100)
        else:
            final_price = float(course.price or 0.0)

        # Проверка доступа к курсу
        if course.is_free:
            has_access = True  # Бесплатный курс — доступен всем
        elif user_id:
            result = await db.execute(
                select(CourseAccess).where(
                    CourseAccess.user_id == user_id,
                    CourseAccess.course_id == course.id
                )
            )
            has_access = result.scalar_one_or_none() is not None  # Проверка покупки
        else:
            has_access = False  # Неавторизованный пользователь и курс платный

        result_list.append({
            "id": course.id,
            "title": course.title,
            "short_description": course.short_description,
            "image": course.image,
            "is_free": course.is_free,
            "price": float(course.price or 0.0),
            "discount": float(course.discount or 0),
            "final_price": round(final_price, 2),
            "has_access": has_access,
            "button_text": "ОТКРЫТЬ" if has_access else "ОТКРЫТЬ",  # Кнопка в зависимости от доступа
            "order": course.order,
            "is_discount_active": is_discount_active,  # Флаг активности скидки (для бейджа или метки)
        })

    return result_list






@router.get("/{course_id}/", response_model=CourseDetailSchema, summary="Детали курса")
async def course_detail(course_id: int, request: Request, db: AsyncSession = Depends(get_db_session)):
    user_id = None

    # Пробуем получить ID пользователя из запроса (если авторизован)
    try:
        user_id = get_current_user_id(request)
    except:
        pass  # Неавторизован — допускаем просмотр страницы

    # Ищем курс по ID
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    # Определяем, активна ли скидка и сколько осталось до её окончания
    is_discount_active, discount_ends_in = get_discount_info(course)

    # Высчитываем финальную цену с учётом скидки (если она активна)
    if is_discount_active:
        final_price = float(course.price or 0.0) * (1 - float(course.discount or 0) / 100)
    else:
        final_price = float(course.price or 0.0)

    # Проверяем, есть ли у пользователя доступ к курсу
    if course.is_free:
        has_access = True  # Бесплатный курс доступен всем
    elif user_id:
        result = await db.execute(
            select(CourseAccess).where(
                CourseAccess.user_id == user_id,
                CourseAccess.course_id == course.id
            )
        )
        has_access = result.scalar_one_or_none() is not None
    else:
        has_access = False  # Пользователь не авторизован и курс платный

    # Формируем и возвращаем ответ
    return {
        "id": course.id,
        "title": course.title,
        "full_description": course.full_description,
        "short_description": course.short_description,
        "image": course.image,
        "is_free": course.is_free,
        "price": float(course.price or 0.0),
        "discount": float(course.discount or 0),
        "final_price": round(final_price, 2),
        "has_access": has_access,
        "button_text": "ОТКРЫТЬ" if has_access else "ПЕРЕЙТИ К ОПЛАТЕ",

        # Дополнительная информация
        "video": course.video,
        "video_preview": course.video_preview,
        "banner_text": course.banner_text,
        "banner_color_left": course.banner_color_left,
        "banner_color_right": course.banner_color_right,
        "order": course.order,

        # Информация о скидке
        "is_discount_active": is_discount_active,       # true/false: активна ли скидка сейчас
        "discount_ends_in": discount_ends_in,           # время до окончания скидки в секундах (если активна)
    }



@router.post("/{course_id}/check-access/", summary="Проверка доступа к курсу")
async def check_course_access(course_id: int, request: Request, db: AsyncSession = Depends(get_db_session)):
    """
    Проверяет, есть ли у пользователя доступ к курсу.
    Возвращает информацию о необходимости регистрации или покупки.
    """
    try:
        user_id = get_current_user_id(request)
        
        result = await db.execute(select(Course).where(Course.id == course_id))
        course = result.scalar_one_or_none()
        if not course:
            raise HTTPException(status_code=404, detail="Курс не найден")
        
        # Для бесплатных курсов достаточно авторизации
        if course.is_free:
            return {
                "has_access": True,
                "requires_auth": False,
                "course_type": "free"
            }
        
        # Для платных проверяем покупку
        result = await db.execute(
            select(CourseAccess).where(
                CourseAccess.user_id == user_id,
                CourseAccess.course_id == course_id
            )
        )
        has_access = result.scalar_one_or_none() is not None
        
        return {
            "has_access": has_access,
            "requires_auth": False,
            "course_type": "paid"
        }
        
    except HTTPException:
        # Пользователь не авторизован
        return {
            "has_access": False,
            "requires_auth": True,
            "message": "Необходима регистрация"
        }


@router.post("/{course_id}/buy/", response_model=BuyCourseResponse, summary="Приобрести курс")
@limiter.limit("3/minute")
async def buy_course(course_id: int, request_data: BuyCourseRequest, request: Request, db: AsyncSession = Depends(get_db_session)):
    user_id = get_current_user_id(request)

    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    # Проверяем, есть ли уже доступ
    result = await db.execute(
        select(CourseAccess).where(
            CourseAccess.user_id == user_id,
            CourseAccess.course_id == course_id
        )
    )
    access_exists = result.scalar_one_or_none()
    if access_exists:
        return {"success": True, "message": "Курс уже доступен"}

    # Создаем запись о доступе (и для бесплатных, и для платных)
    new_access = CourseAccess(user_id=user_id, course_id=course_id)
    db.add(new_access)
    await db.commit()

    if course.is_free:
        return {"success": True, "message": "Бесплатный курс успешно открыт"}
    else:
        # Здесь должна быть проверка оплаты по payment_id
        return {"success": True, "message": "Курс успешно приобретён"}