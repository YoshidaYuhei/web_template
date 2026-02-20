from fastapi import APIRouter

from app.api.v1.endpoints import auth
from app.api.v1.internal import health

api_router = APIRouter()

# Public endpoints
api_router.include_router(auth.router)

# Internal endpoints
api_router.include_router(health.router)
