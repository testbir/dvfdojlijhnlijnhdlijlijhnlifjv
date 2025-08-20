# id_service/main.py


from fastapi import FastAPI
from services.jwk_service import jwk_service
from utils import rate_limiter, setup_logging
from services.backchannel_logout import backchannel_logout_service

app = FastAPI()
logger = setup_logging()

@app.on_event("startup")
async def startup():
    await jwk_service.ensure_active_key()
    await rate_limiter.init()

@app.on_event("shutdown")
async def shutdown():
    await backchannel_logout_service.cleanup()
    await rate_limiter.close()
