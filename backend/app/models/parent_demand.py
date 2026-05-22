"""家长需求发布表模型"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class ParentDemand(Base):
    __tablename__ = "parent_demands"

    demand_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="需求ID")
    parent_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, comment="发布人用户ID"
    )
    subjects: Mapped[str] = mapped_column(String(256), nullable=False, comment="辅导科目")
    grade: Mapped[str] = mapped_column(String(32), nullable=False, comment="学生年级")
    address: Mapped[str] = mapped_column(String(256), nullable=False, comment="上课地址")
    address_detail: Mapped[str | None] = mapped_column(String(256), nullable=True, comment="地址详情")
    budget_min: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="预算最低(元/小时)")
    budget_max: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="预算最高(元/小时)")
    frequency: Mapped[str] = mapped_column(String(16), nullable=False, comment="每周上课频率")
    expect_time: Mapped[str | None] = mapped_column(String(256), nullable=True, comment="期望上课时间描述")
    student_note: Mapped[str | None] = mapped_column(Text, nullable=True, comment="学生情况备注")
    teacher_requirement: Mapped[str | None] = mapped_column(Text, nullable=True, comment="对教师要求")
    status: Mapped[str] = mapped_column(
        Enum("open", "closed", "matched", name="demand_status_enum"),
        nullable=False,
        default="open",
        comment="状态: open=开放中, closed=已关闭, matched=已匹配",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="发布时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )
