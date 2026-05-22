"""认证 API — 微信登录 / 手机号绑定 / 身份选择"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps.auth import get_current_user
from app.services.auth_service import AuthService
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    BindPhoneRequest,
    SelectRoleRequest,
    UpdateProfileRequest,
    LoginResponse,
    BindPhoneResponse,
    SelectRoleResponse,
    UserInfo,
)
from app.schemas.common import APIResponse

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=APIResponse[LoginResponse])
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """微信登录 — code 换 token"""
    svc = AuthService(db)
    result = await svc.login(req.code)
    return APIResponse.success(data=result)


@router.post("/bind-phone", response_model=APIResponse[BindPhoneResponse])
async def bind_phone(
    req: BindPhoneRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """绑定手机号"""
    svc = AuthService(db)
    result = await svc.bind_phone(user, req.code)
    return APIResponse.success(data=result)


@router.post("/select-role", response_model=APIResponse[SelectRoleResponse])
async def select_role(
    req: SelectRoleRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """选择身份 (只能选一次)"""
    svc = AuthService(db)
    result = await svc.select_role(user, req.role)
    return APIResponse.success(data=result)


@router.get("/profile", response_model=APIResponse[UserInfo])
async def get_profile(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取当前用户信息"""
    svc = AuthService(db)
    result = await svc.get_profile(user)
    return APIResponse.success(data=result)


@router.put("/profile", response_model=APIResponse[UserInfo])
async def update_profile(
    req: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新用户信息"""
    svc = AuthService(db)
    result = await svc.update_profile(user, req.nickname, req.avatar_url)
    return APIResponse.success(data=result)


# TODO: POST /auth/refresh — 刷新 Token (P1)
