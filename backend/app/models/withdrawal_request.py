"""提现申请表模型"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, DECIMAL, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class WithdrawalRequest(Base):
    __tablename__ = "withdrawal_requests"

    withdrawal_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="提现ID")
    teacher_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("teachers.teacher_id", ondelete="RESTRICT"), nullable=False, comment="教师ID"
    )
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False, comment="提现金额(元)")
    fee: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False, default=Decimal("0.00"), comment="手续费(元)")
    actual_amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False, comment="实际到账金额(元)")
    status: Mapped[str] = mapped_column(
        Enum("pending", "approved", "rejected", "paid", name="withdrawal_status_enum"),
        nullable=False,
        default="pending",
        comment="状态",
    )
    audit_reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="审核原因")
    wx_transfer_id: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="微信企业付款流水号")
    audited_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="审核时间")
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="打款时间")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="申请时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )
