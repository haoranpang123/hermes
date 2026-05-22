"""评价表模型"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class Review(Base):
    __tablename__ = "reviews"

    review_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="评价ID")
    order_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orders.order_id", ondelete="RESTRICT"), unique=True, nullable=False, comment="关联订单ID"
    )
    parent_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False, comment="评价人(家长)用户ID"
    )
    teacher_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("teachers.teacher_id", ondelete="RESTRICT"), nullable=False, comment="被评价教师ID"
    )
    teaching_ability: Mapped[int] = mapped_column(Integer, nullable=False, comment="教学能力 1-5星")
    communication: Mapped[int] = mapped_column(Integer, nullable=False, comment="沟通态度 1-5星")
    punctuality: Mapped[int] = mapped_column(Integer, nullable=False, comment="是否准时 1-5星")
    content: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="文字评价")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="评价时间"
    )

    order: Mapped["Order"] = relationship("Order", back_populates="review")
