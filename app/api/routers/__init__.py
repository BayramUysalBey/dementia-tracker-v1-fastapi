from fastapi import APIRouter
from app.api.routers import users, status

api_router = APIRouter()
api_router.include_router(users.router, prefix="/v1/users", tags=["Users"])
api_router.include_router(status.router, prefix="/v1/status", tags=["Status"])
