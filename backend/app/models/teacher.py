"""教师扩展信息表模型"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, DECIMAL, Text, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class Teacher(Base):
    __tablename__ = "teachers"

    teacher_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="教师ID")
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False, comment="关联用户ID"
    )
    real_name: Mapped[str] = mapped_column(String(32), nullable=False, comment="真实姓名")
    gender: Mapped[str] = mapped_column(
        Enum("male", "female", name="gender_enum"), nullable=False, comment="性别"
    )
    university: Mapped[str] = mapped_column(String(64), nullable=False, default="河南大学", comment="学校")
    major: Mapped[str] = mapped_column(String(64), nullable=False, comment="专业")
    grade: Mapped[str] = mapped_column(String(16), nullable=False, comment="年级")
    bio: Mapped[str | None] = mapped_column(Text, nullable=True, comment="个人简介")
    min_price: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="最低课时费(元/小时)")
    teaching_regions: Mapped[str | None] = mapped_column(String(512), nullable=True, comment="可授课区域JSON数组")
    avg_rating: Mapped[Decimal] = mapped_column(
        DECIMAL(3, 2), nullable=False, default=Decimal("0.00"), comment="平均评分"
    )
    review_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="评价总数")
    is_available: Mapped[int] = mapped_column(Integer, nullable=False, default=1, comment="当前是否可预约: 1=可, 0=否")
    audit_status: Mapped[str] = mapped_column(
        Enum("pending", "approved", "rejected", name="audit_status_enum"),
        nullable=False,
        default="pending",
        comment="审核状态",
    )
    audit_reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="审核原因")
    audited_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="审核时间")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="申请时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="teacher")
    certificates: Mapped[list["TeacherCertificate"]] = relationship(
        "TeacherCertificate", back_populates="teacher", lazy="selectin", cascade="all, delete-orphan"
    )
    subjects: Mapped[list["TeacherSubject"]] = relationship(
        "TeacherSubject", back_populates="teacher", lazy="selectin", cascade="all, delete-orphan"
    )
    schedules: Mapped[list["TeacherSchedule"]] = relationship(
        "TeacherSchedule", back_populates="teacher", lazy="selectin", cascade="all, delete-orphan"
    )
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="teacher", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Teacher(teacher_id={self.teacher_id}, real_name={self.real_name})>"
