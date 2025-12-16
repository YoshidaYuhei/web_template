from fastapi import APIRouter

from app.api.v1.endpoints import auth, users
from app.api.v1.internal import health

api_router = APIRouter()

# Internal endpoints
api_router.include_router(health.router)

# Public endpoints
api_router.include_router(auth.router)
api_router.include_router(users.router)
