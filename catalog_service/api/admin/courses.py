from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.dependencies import get_db_session
from models.course import Course
from schemas.course import CourseCreate

router = APIRouter(prefix="/courses")

@router.post("/", summary="Создать курс")
async def admin_create_course(data: CourseCreate, db: AsyncSession = Depends(get_db_session)):
    course = Course(**data.model_dump(mode="python"))
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return {"id": course.id, "message": "Курс создан"}

@router.put("/{course_id}", summary="Обновить курс")
async def admin_update_course(course_id: int, data: CourseCreate, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(Course).where(Course.id == course_id))
    course = res.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    for k, v in data.model_dump(mode="python", exclude_unset=True).items():
        if isinstance(v, str) and not v.strip():
            v = None
        setattr(course, k, v)
    await db.commit()
    await db.refresh(course)
    return {"id": course.id, "message": "Курс обновлён"}

@router.delete("/{course_id}", summary="Удалить курс")
async def admin_delete_course(course_id: int, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(Course).where(Course.id == course_id))
    course = res.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    await db.delete(course)
    await db.commit()
    return {"message": "Курс удалён"}

@router.get("/{course_id}", response_model=CourseCreate, summary="Получить курс (админ)")
async def admin_get_course(course_id: int, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(Course).where(Course.id == course_id))
    course = res.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    return course

@router.patch("/{course_id}/discount", summary="Применить скидку")
async def apply_course_discount(course_id: int, discount: float = Body(..., embed=True), db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(Course).where(Course.id == course_id))
    course = res.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    if not 0 <= discount <= 100:
        raise HTTPException(status_code=400, detail="Скидка должна быть от 0 до 100")
    course.discount = discount
    await db.commit()
    return {"success": True, "discount": discount}

@router.patch("/{course_id}/order", summary="Изменить порядок курса")
async def update_course_order(course_id: int, order: int = Body(..., embed=True), db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(Course).where(Course.id == course_id))
    course = res.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    course.order = order
    await db.commit()
    return {"success": True, "order": order}

@router.post("/{course_id}/duplicate", summary="Дублировать курс (метаданные)")
async def duplicate_course(course_id: int, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(Course).where(Course.id == course_id))
    original = res.scalar_one_or_none()
    if not original:
        raise HTTPException(status_code=404, detail="Курс не найден")

    new_course = Course(
        title=f"{original.title} (копия)",
        short_description=original.short_description,
        full_description=original.full_description,
        image=original.image,
        is_free=original.is_free,
        price=original.price,
        discount=original.discount,
        video=original.video,
        video_preview=original.video_preview,
        banner_text=original.banner_text,
        banner_color_left=original.banner_color_left,
        banner_color_right=original.banner_color_right,
        group_title=original.group_title,
        order=(original.order or 0) + 1
    )
    db.add(new_course)
    await db.commit()
    return {"id": new_course.id, "message": "Курс успешно дублирован"}
