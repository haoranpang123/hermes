"""收藏表模型"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("parent_id", "teacher_id", name="uk_parent_teacher"),
    )

    fav_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="收藏ID")
    parent_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, comment="家长用户ID"
    )
    teacher_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("teachers.teacher_id", ondelete="CASCADE"), nullable=False, comment="教师ID"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="收藏时间"
    )
