"""SQLAlchemy 模型基类和汇总导出"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 声明式基类"""
    pass


# 所有模型在此集中导入，确保 Alembic 能发现
from app.models.user import User
from app.models.admin_user import AdminUser
from app.models.teacher import Teacher
from app.models.teacher_certificate import TeacherCertificate
from app.models.teacher_subject import TeacherSubject
from app.models.teacher_schedule import TeacherSchedule
from app.models.order import Order
from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction
from app.models.review import Review
from app.models.favorite import Favorite
from app.models.parent_demand import ParentDemand
from app.models.withdrawal_request import WithdrawalRequest
from app.models.system_config import SystemConfig

__all__ = [
    "Base",
    "User",
    "AdminUser",
    "Teacher",
    "TeacherCertificate",
    "TeacherSubject",
    "TeacherSchedule",
    "Order",
    "Wallet",
    "WalletTransaction",
    "Review",
    "Favorite",
    "ParentDemand",
    "WithdrawalRequest",
    "SystemConfig",
]
