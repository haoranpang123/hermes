"""API v1 路由汇总"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.teachers import router as teachers_router
from app.api.v1.teacher import router as teacher_router
from app.api.v1.orders import router as orders_router
from app.api.v1.wallet import router as wallet_router
from app.api.v1.demands import router as demands_router
from app.api.v1.admin import router as admin_router

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(auth_router)
v1_router.include_router(teachers_router)
v1_router.include_router(teacher_router)
v1_router.include_router(orders_router)
v1_router.include_router(wallet_router)
v1_router.include_router(demands_router)
v1_router.include_router(admin_router)
