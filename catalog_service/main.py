# catalog_service/main.py

from fastapi import FastAPI, Depends
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from api.public import courses as public_courses, accounts as public_accounts, promocodes as public_promocodes, extras as public_extras
from api.admin import courses as admin_courses, lead_magnets as admin_lead_magnets, banner as admin_banner, promo as admin_promo, promocodes as admin_promocodes, course_modal as admin_course_modal, student_works as admin_student_works
from api.internal import access as internal_access, users as internal_users, statistics as internal_statistics
from api.public import banners as public_banners
from api import health as health_api
from utils.admin_auth import AdminAuth

# ⬇️ подключаем лимитер
from slowapi.errors import RateLimitExceeded
from utils.rate_limit import limiter, custom_rate_limit_handler

load_dotenv()
app = FastAPI(title="Catalog Service")

# ⬇️ wiring для slowapi
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... остальное без изменений


# public
app.include_router(public_courses.router,   prefix="/v1/public", tags=["Public - Courses"])
app.include_router(public_accounts.router,  prefix="/v1/public", tags=["Public - Accounts"])
app.include_router(public_promocodes.router,prefix="/v1/public", tags=["Public - Promocodes"])
app.include_router(public_extras.router,    prefix="/v1/public", tags=["Public - Extras"])
app.include_router(public_banners.router,    prefix="/v1/public", tags=["Public - Banners"])

# admin (защита INTERNAL_TOKEN)
deps = [Depends(AdminAuth())]
app.include_router(admin_courses.router,      prefix="/v1/admin", tags=["Admin - Courses"],       dependencies=deps)
app.include_router(admin_lead_magnets.router, prefix="/v1/admin", tags=["Admin - Lead Magnets"],  dependencies=deps)
app.include_router(admin_banner.router,       prefix="/v1/admin", tags=["Admin - Banners"],       dependencies=deps)
app.include_router(admin_promo.router,        prefix="/v1/admin", tags=["Admin - Promo"],         dependencies=deps)
app.include_router(admin_promocodes.router,   prefix="/v1/admin", tags=["Admin - Promocodes"],    dependencies=deps)
app.include_router(admin_course_modal.router, prefix="/v1/admin", tags=["Admin - Course Modals"], dependencies=deps)
app.include_router(admin_student_works.router,prefix="/v1/admin", tags=["Admin - Student Works"], dependencies=deps)

# internal
app.include_router(internal_access.router,     prefix="/v1/internal", tags=["Internal - Access"])
app.include_router(internal_users.router,      prefix="/v1/internal", tags=["Internal - Users"])
app.include_router(internal_statistics.router, prefix="/v1/internal", tags=["Internal - Statistics"])

# health
app.include_router(health_api.router, tags=["Health"])
