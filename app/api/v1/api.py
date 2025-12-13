from fastapi import APIRouter

from app.api.v1.internal import health

api_router = APIRouter()

# Internal endpoints
api_router.include_router(health.router)
