"""API 层认证依赖注入"""

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.models.user import User

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """从 JWT 中提取当前登录用户"""
    if credentials is None:
        raise UnauthorizedError("请先登录")

    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError as e:
        raise UnauthorizedError(str(e))

    user_id = int(payload.get("sub", 0))
    if not user_id:
        raise UnauthorizedError("无效的登录凭证")

    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise UnauthorizedError("用户不存在")
    if user.status == 0:
        raise UnauthorizedError("账号已被禁用")

    return user


def require_role(role: str):
    """角色守卫工厂函数"""

    async def role_dependency(user: User = Depends(get_current_user)) -> User:
        if user.role != role:
            raise ForbiddenError(f"需要 {role} 角色")
        return user

    return role_dependency


# 预定义角色守卫
require_parent = require_role("parent")
require_teacher = require_role("teacher")
require_admin = require_role("admin")
