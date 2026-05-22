"""管理员表模型"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class AdminUser(Base):
    __tablename__ = "admin_users"

    admin_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="管理员ID")
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False, comment="关联用户ID"
    )
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, comment="登录用户名")
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False, comment="密码哈希(bcrypt)")
    real_name: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="管理员姓名")
    status: Mapped[int] = mapped_column(Integer, nullable=False, default=1, comment="1=正常, 0=禁用")
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="最后登录时间")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )

    user: Mapped["User"] = relationship("User", back_populates="admin_user")

    def __repr__(self) -> str:
        return f"<AdminUser(admin_id={self.admin_id}, username={self.username})>"
