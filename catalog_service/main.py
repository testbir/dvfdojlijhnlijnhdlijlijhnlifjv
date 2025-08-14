# catalog_service/main.py

from fastapi import FastAPI
from dotenv import load_dotenv
from catalog_service.db.init_db import init_db
from fastapi.middleware.cors import CORSMiddleware

# rate limit
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from catalog_service.utils.rate_limit import limiter, custom_rate_limit_handler

# routers
from catalog_service.api.public import courses as public_courses, extras as public_extras, accounts as public_accounts, promocodes as public_promocodes
from catalog_service.api.admin import courses as admin_courses, lead_magnets as admin_lead_magnets, banner as admin_banner, promo as admin_promo, promocodes as admin_promocode, course_modal as admin_course_modal, student_works as admin_student_works
from catalog_service.api.internal import access as internal_access, users as internal_users, statistics as internal_statistics

# logs
from catalog_service.utils.monitoring import log_requests

load_dotenv()
app = FastAPI(title="Course Catalog")

app.middleware("http")(log_requests)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=False,
    allow_methods=["*"], allow_headers=["*"],
)

# SlowAPI
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)
app.add_middleware(SlowAPIMiddleware)

# public
app.include_router(public_courses.router,     prefix="/v1/public",  tags=["Public - Courses"])
app.include_router(public_extras.router,      prefix="/v1/public",  tags=["Public - Extras"])
app.include_router(public_accounts.router,    prefix="/v1/public",  tags=["Public - Accounts"])
app.include_router(public_promocodes.router,  prefix="/v1/public",  tags=["Public - Promocodes"])

# admin
app.include_router(admin_courses.router,        prefix="/v1/admin",   tags=["Admin - Courses"])
app.include_router(admin_lead_magnets.router,   prefix="/v1/admin",   tags=["Admin - Lead Magnets"])
app.include_router(admin_banner.router,         prefix="/v1/admin",   tags=["Admin - Banners"])
app.include_router(admin_promo.router,          prefix="/v1/admin",   tags=["Admin - Promos"])
app.include_router(admin_promocode.router,      prefix="/v1/admin",   tags=["Admin - Promocodes"])
app.include_router(admin_course_modal.router,   prefix="/v1/admin",   tags=["Admin - Course Modals"])
app.include_router(admin_student_works.router,  prefix="/v1/admin",   tags=["Admin - Student Works"])

# internal
app.include_router(internal_access.router,      prefix="/v1/internal", tags=["Internal - Access"])
app.include_router(internal_users.router,       prefix="/v1/internal", tags=["Internal - Users"])
app.include_router(internal_statistics.router,  prefix="/v1/internal", tags=["Internal - Statistics"])
