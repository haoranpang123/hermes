"""用户表模型"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, String, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="用户ID")
    openid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, comment="微信OpenID")
    unionid: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="微信UnionID")
    nickname: Mapped[str] = mapped_column(String(64), nullable=False, comment="微信昵称")
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True, comment="微信头像URL")
    phone: Mapped[str | None] = mapped_column(String(11), nullable=True, comment="绑定手机号")
    role: Mapped[str | None] = mapped_column(
        Enum("parent", "teacher", "admin", name="user_role_enum"),
        nullable=True,
        comment="角色: parent=家长, teacher=教师, admin=管理员",
    )
    status: Mapped[int] = mapped_column(Integer, nullable=False, default=1, comment="状态: 1=正常, 0=禁用")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="注册时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    # 关系
    teacher: Mapped["Teacher | None"] = relationship("Teacher", back_populates="user", uselist=False, lazy="selectin")
    wallet: Mapped["Wallet | None"] = relationship("Wallet", back_populates="user", uselist=False, lazy="selectin")
    admin_user: Mapped["AdminUser | None"] = relationship("AdminUser", back_populates="user", uselist=False, lazy="selectin")

    def __repr__(self) -> str:
        return f"<User(user_id={self.user_id}, nickname={self.nickname}, role={self.role})>"
