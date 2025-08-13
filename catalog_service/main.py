# catalog_service/main.py

from fastapi import FastAPI
from dotenv import load_dotenv
from catalog_service.api.public import accounts
from db.init_db import init_db
from core.config import settings

from utils.rate_limit import limiter, custom_rate_limit_handler
from fastapi.middleware.cors import CORSMiddleware


from api.public import courses as public_courses, extras as public_extras, accounts as public_accounts
from api.admin import courses as admin_courses, lead_magnets as admin_lead_magnets
from api.internal import access as internal_access, users as internal_users, statistics as internal_statistics


load_dotenv()

app = FastAPI(title="Course Catalog")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await init_db()

app.state.limiter = limiter

# Основные роутеры

# public
app.include_router(public_courses.router,  prefix="/v1/public",  tags=["Courses"])
app.include_router(public_extras.router,   prefix="/v1/public",  tags=["Public Course Extras"])
app.include_router(public_accounts.router, prefix="/v1/public",  tags=["User Accounts"])

# admin
app.include_router(admin_courses.router,        prefix="/v1/admin",   tags=["Admin - Courses"])
app.include_router(admin_lead_magnets.router,   prefix="/v1/admin",   tags=["Admin - Lead Magnets"])

# internal
app.include_router(internal_access.router,      prefix="/v1/internal", tags=["Internal - Access"])
app.include_router(internal_users.router,       prefix="/v1/internal", tags=["Internal - Users"])
app.include_router(internal_statistics.router,  prefix="/v1/internal", tags=["Internal - Statistics"])

