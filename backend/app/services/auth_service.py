"""认证服务 — 微信登录 / 手机号绑定 / 身份选择"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessError, ValidationError
from app.core.security import create_access_token, decode_access_token
from app.core.wechat import WechatAPI
from app.models.user import User
from app.models.wallet import Wallet
from app.schemas.auth import (
    LoginResponse,
    BindPhoneResponse,
    SelectRoleResponse,
    UserInfo,
)


class AuthService:
    """认证服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.wechat = WechatAPI()

    async def login(self, code: str) -> LoginResponse:
        """
        微信登录流程:
        1. code → openid
        2. 查找或创建用户
        3. 签发 JWT
        """
        if not code:
            raise ValidationError("code 不能为空")

        # Mock 模式: 如果微信配置为空，使用 mock
        if not self.wechat.app_id:
            openid = f"mock_openid_{uuid.uuid4().hex[:12]}"
            session_key = "mock_session_key"
        else:
            wx_data = await self.wechat.code2session(code)
            openid = wx_data["openid"]
            session_key = wx_data["session_key"]

        # 查找已有用户
        result = await self.db.execute(select(User).where(User.openid == openid))
        user = result.scalar_one_or_none()

        is_new = False
        if user is None:
            is_new = True
            user = User(
                openid=openid,
                nickname="微信用户",
                avatar_url=None,
                role=None,
                status=1,
            )
            self.db.add(user)
            await self.db.flush()

            # 创建钱包
            wallet = Wallet(user_id=user.user_id, balance=0)
            self.db.add(wallet)

        # 签发 JWT
        token = create_access_token(user_id=user.user_id, role=user.role)

        user_info = UserInfo(
            user_id=user.user_id,
            nickname=user.nickname or "微信用户",
            avatar_url=user.avatar_url,
            phone=user.phone,
            role=user.role,
            has_selected_role=user.role is not None,
        )

        return LoginResponse(
            token=token,
            user_info=user_info,
            is_new=is_new,
        )

    async def bind_phone(self, user: User, code: str) -> BindPhoneResponse:
        """
        绑定手机号
        MVP 阶段: 简化处理，直接用 code 作为 mock 手机号
        生产环境需要调用微信解密 API
        """
        if user.phone:
            raise BusinessError("已绑定手机号，无需重复绑定")

        # MVP: mock — 生产环境需解密微信 code
        mock_phone = f"138{user.user_id:08d}"[-11:]
        user.phone = mock_phone
        await self.db.flush()

        return BindPhoneResponse(phone=f"{mock_phone[:3]}****{mock_phone[-4:]}")

    async def select_role(self, user: User, role: str) -> SelectRoleResponse:
        """选择身份 (只能选一次)"""
        if user.role is not None:
            raise BusinessError("已选择过身份，不可更改")

        if role not in ("parent", "teacher"):
            raise ValidationError("role 必须为 parent 或 teacher")

        user.role = role
        await self.db.flush()

        # 签发新 token (带角色)
        token = create_access_token(user_id=user.user_id, role=role)

        return SelectRoleResponse(
            user_id=user.user_id,
            role=role,
            need_teacher_apply=(role == "teacher"),
        )

    async def get_profile(self, user: User) -> UserInfo:
        """获取当前用户信息"""
        return UserInfo(
            user_id=user.user_id,
            nickname=user.nickname,
            avatar_url=user.avatar_url,
            phone=user.phone,
            role=user.role,
            has_selected_role=user.role is not None,
        )

    async def update_profile(self, user: User, nickname: str | None, avatar_url: str | None) -> UserInfo:
        """更新用户信息"""
        if nickname is not None:
            user.nickname = nickname
        if avatar_url is not None:
            user.avatar_url = avatar_url
        await self.db.flush()

        return UserInfo(
            user_id=user.user_id,
            nickname=user.nickname,
            avatar_url=user.avatar_url,
            phone=user.phone,
            role=user.role,
            has_selected_role=user.role is not None,
        )
