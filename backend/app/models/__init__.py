"""
河大家教小程序 — SQLAlchemy 数据模型包

所有数据库模型的基类和统一导出。
"""

from sqlalchemy.orm import declarative_base

# SQLAlchemy 2.0 声明式基类
Base = declarative_base()

# 延迟导入模型，避免循环引用
# 在实际开发中，取消注释并创建对应模块：

# from app.models.user import User
# from app.models.teacher import Teacher, TeacherCertificate, TeacherSubject, TeacherSchedule
# from app.models.order import Order
# from app.models.wallet import Wallet, WalletTransaction
# from app.models.review import Review
# from app.models.demand import ParentDemand
# from app.models.favorite import Favorite
# from app.models.withdrawal import WithdrawalRequest
# from app.models.system_config import SystemConfig

__all__ = [
    "Base",
    # "User",
    # "Teacher",
    # "TeacherCertificate",
    # "TeacherSubject",
    # "TeacherSchedule",
    # "Order",
    # "Wallet",
    # "WalletTransaction",
    # "Review",
    # "ParentDemand",
    # "Favorite",
    # "WithdrawalRequest",
    # "SystemConfig",
]
