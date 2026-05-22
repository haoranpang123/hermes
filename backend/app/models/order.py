"""订单表模型"""

from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import BigInteger, Date, DateTime, DECIMAL, ForeignKey, Integer, String, Text, Time as SATime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="订单ID")
    order_no: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, comment="订单编号")
    parent_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False, comment="家长用户ID"
    )
    teacher_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("teachers.teacher_id", ondelete="RESTRICT"), nullable=False, comment="教师ID"
    )
    subject: Mapped[str] = mapped_column(String(32), nullable=False, comment="科目")
    grade: Mapped[str] = mapped_column(String(32), nullable=False, comment="年级")
    lesson_date: Mapped[date] = mapped_column(Date, nullable=False, comment="上课日期")
    start_time: Mapped[time] = mapped_column(SATime, nullable=False, comment="开始时间")
    end_time: Mapped[time] = mapped_column(SATime, nullable=False, comment="结束时间")
    duration: Mapped[Decimal] = mapped_column(DECIMAL(4, 1), nullable=False, comment="课时长度(小时)")
    unit_price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False, comment="单价(元/小时)")
    total_amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False, comment="订单总金额(元)")
    commission_rate: Mapped[Decimal] = mapped_column(
        DECIMAL(5, 3), nullable=False, default=Decimal("0.150"), comment="佣金比例"
    )
    commission_amount: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), nullable=False, default=Decimal("0.00"), comment="佣金金额(元)"
    )
    settlement_amount: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), nullable=False, default=Decimal("0.00"), comment="教师结算金额(元)"
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending_confirm", comment="订单状态"
    )
    pay_transaction_id: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="微信支付流水号")
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="支付时间")
    teacher_accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="教师确认接单时间")
    teacher_started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="教师标记上课时间")
    teacher_completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="教师标记完成时间")
    parent_confirm_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="家长确认时间")
    auto_confirm_deadline: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="自动确认截止时间"
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="订单完成时间")
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="订单取消时间")
    cancel_reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="取消/退款原因")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )

    # 关系
    teacher: Mapped["Teacher"] = relationship("Teacher", back_populates="orders")
    review: Mapped["Review | None"] = relationship("Review", back_populates="order", uselist=False, lazy="selectin")

    def __repr__(self) -> str:
        return f"<Order(order_id={self.order_id}, order_no={self.order_no}, status={self.status})>"
