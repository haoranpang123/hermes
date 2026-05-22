"""虚拟币钱包表模型"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class Wallet(Base):
    __tablename__ = "wallets"

    wallet_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="钱包ID")
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False, comment="用户ID"
    )
    balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="虚拟币余额")
    total_recharged: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="累计充值币数")
    total_spent: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="累计消费币数")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )

    user: Mapped["User"] = relationship("User", back_populates="wallet")
