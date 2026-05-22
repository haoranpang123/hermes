"""钱包模块 Schemas"""

from pydantic import BaseModel, Field


class WalletOverview(BaseModel):
    balance: int = 0
    total_recharged: int = 0
    total_spent: int = 0


class RechargeRequest(BaseModel):
    amount: int = Field(..., ge=1, le=1000, description="充值金额(元)")


class RechargeResponse(BaseModel):
    recharge_id: int
    amount: int
    coins: int
    wechat_pay_params: dict | None = None


class TransactionItem(BaseModel):
    transaction_id: int
    type: str
    amount: int
    balance_after: int
    description: str
    created_at: str
