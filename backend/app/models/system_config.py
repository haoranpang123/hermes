"""系统配置表模型"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class SystemConfig(Base):
    __tablename__ = "system_configs"

    config_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="配置ID")
    config_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, comment="配置键")
    config_value: Mapped[str] = mapped_column(Text, nullable=False, comment="配置值")
    description: Mapped[str | None] = mapped_column(String(256), nullable=True, comment="配置说明")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )
