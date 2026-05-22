"""虚拟币交易流水表模型"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    transaction_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="流水ID")
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, comment="用户ID"
    )
    type: Mapped[str] = mapped_column(
        Enum("recharge", "consume", "refund", name="transaction_type_enum"),
        nullable=False,
        comment="交易类型: recharge=充值, consume=消费, refund=退款",
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False, comment="变动币数")
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False, comment="变动后余额")
    description: Mapped[str] = mapped_column(String(256), nullable=False, comment="描述")
    ref_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="关联业务ID")
    ref_type: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="关联业务类型")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )
