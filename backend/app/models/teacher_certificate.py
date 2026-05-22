"""教师资质证书表模型"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class TeacherCertificate(Base):
    __tablename__ = "teacher_certificates"

    cert_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="证书ID")
    teacher_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("teachers.teacher_id", ondelete="CASCADE"), nullable=False, comment="关联教师ID"
    )
    cert_type: Mapped[str] = mapped_column(String(32), nullable=False, comment="证书类型: student_card, other")
    image_url: Mapped[str] = mapped_column(String(512), nullable=False, comment="证书图片URL")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="排序")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )

    teacher: Mapped["Teacher"] = relationship("Teacher", back_populates="certificates")
