"""认证模块 Schemas"""

from pydantic import BaseModel, Field


# ---- 请求 ----

class LoginRequest(BaseModel):
    """微信登录请求"""
    code: str = Field(..., min_length=1, description="微信 wx.login() 返回的 code")


class BindPhoneRequest(BaseModel):
    """绑定手机号请求"""
    code: str = Field(..., min_length=1, description="微信 getPhoneNumber 返回的 code")


class SelectRoleRequest(BaseModel):
    """选择身份请求"""
    role: str = Field(..., pattern="^(parent|teacher)$", description="身份: parent 或 teacher")


class UpdateProfileRequest(BaseModel):
    """更新用户信息请求"""
    nickname: str | None = Field(None, max_length=64)
    avatar_url: str | None = Field(None, max_length=512)


class AdminLoginRequest(BaseModel):
    """管理后台登录请求"""
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)


# ---- 响应 ----

class UserInfo(BaseModel):
    """用户简要信息"""
    user_id: int
    nickname: str
    avatar_url: str | None = None
    phone: str | None = None
    role: str | None = None
    has_selected_role: bool = False


class LoginResponse(BaseModel):
    """登录响应"""
    token: str
    user_info: UserInfo
    is_new: bool = False


class BindPhoneResponse(BaseModel):
    """绑定手机号响应"""
    phone: str


class SelectRoleResponse(BaseModel):
    """选择身份响应"""
    user_id: int
    role: str
    need_teacher_apply: bool = False


class AdminLoginResponse(BaseModel):
    """管理员登录响应"""
    token: str
    admin_info: dict
