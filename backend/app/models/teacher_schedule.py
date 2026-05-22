"""教师可授课时间表模型"""

from datetime import datetime, time

from sqlalchemy import BigInteger, DateTime, ForeignKey, Enum, Time, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class TeacherSchedule(Base):
    __tablename__ = "teacher_schedules"

    schedule_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="排课ID")
    teacher_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("teachers.teacher_id", ondelete="CASCADE"), nullable=False, comment="关联教师ID"
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False, comment="星期: 1=周一, 7=周日")
    start_time: Mapped[time] = mapped_column(Time, nullable=False, comment="开始时间")
    end_time: Mapped[time] = mapped_column(Time, nullable=False, comment="结束时间")
    status: Mapped[str] = mapped_column(
        Enum("available", "occupied", "blocked", name="schedule_status_enum"),
        nullable=False,
        default="available",
        comment="状态: available=可约, occupied=已约, blocked=临时关闭",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )

    teacher: Mapped["Teacher"] = relationship("Teacher", back_populates="schedules")
