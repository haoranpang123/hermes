"""教师教学科目表模型"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class TeacherSubject(Base):
    __tablename__ = "teacher_subjects"
    __table_args__ = (
        UniqueConstraint("teacher_id", "subject", "grade_level", name="uk_teacher_subject_grade"),
    )

    subj_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="科目关联ID")
    teacher_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("teachers.teacher_id", ondelete="CASCADE"), nullable=False, comment="关联教师ID"
    )
    subject: Mapped[str] = mapped_column(String(32), nullable=False, comment="教学科目")
    grade_level: Mapped[str] = mapped_column(String(32), nullable=False, comment="教学年级")
    unit_price: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="该科目课时费(元/小时)")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )

    teacher: Mapped["Teacher"] = relationship("Teacher", back_populates="subjects")
