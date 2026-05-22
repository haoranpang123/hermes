"""应用配置管理 — 从环境变量/.env读取"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """全局配置"""

    # ---- App ----
    APP_NAME: str = "河大家教"
    DEBUG: bool = False
    SECRET_KEY: str = "dev-secret-key-change-in-production"

    # ---- Database ----
    DATABASE_URL: str = "mysql+aiomysql://root:password@localhost:3306/henu_tutor"

    # ---- Redis ----
    REDIS_URL: str = "redis://localhost:6379/0"

    # ---- WeChat Mini Program ----
    WX_APP_ID: str = ""
    WX_APP_SECRET: str = ""

    # ---- WeChat Pay V3 ----
    WXPAY_MCH_ID: str = ""
    WXPAY_API_V3_KEY: str = ""
    WXPAY_SERIAL_NO: str = ""
    WXPAY_PRIVATE_KEY_PATH: str = ""
    WXPAY_NOTIFY_URL: str = ""

    # ---- JWT ----
    JWT_SECRET_KEY: str = "dev-jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24

    # ---- Tencent Cloud (P1) ----
    TENCENT_SECRET_ID: str = ""
    TENCENT_SECRET_KEY: str = ""
    TENCENT_IM_SDK_APP_ID: str = ""

    # ---- Business ----
    DEFAULT_COMMISSION_RATE: float = 0.15
    CONTACT_COIN_PRICE: int = 5
    AUTO_CONFIRM_HOURS: int = 48
    TEACHER_RESPONSE_HOURS: int = 24
    MIN_WITHDRAWAL_AMOUNT: float = 10.00
    CONTACT_VIEW_EXPIRE_DAYS: int = 7

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """获取全局配置单例"""
    return Settings()
