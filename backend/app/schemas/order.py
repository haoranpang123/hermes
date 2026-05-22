"""订单模块 Schemas"""

from pydantic import BaseModel, Field


class CreateOrderRequest(BaseModel):
    """创建订单请求"""
    teacher_id: int = Field(..., gt=0)
    subject: str = Field(..., max_length=32)
    grade: str = Field(..., max_length=32)
    lesson_date: str = Field(..., description="格式 YYYY-MM-DD")
    start_time: str = Field(..., description="格式 HH:MM")
    end_time: str = Field(..., description="格式 HH:MM")
    address: str | None = Field(None, max_length=256)


class CreateOrderResponse(BaseModel):
    order_id: int
    order_no: str
    total_amount: float
    wechat_pay_params: dict | None = None


class OrderListItem(BaseModel):
    order_id: int
    order_no: str
    teacher_id: int | None = None
    parent_id: int | None = None
    teacher_name: str = ""
    subject: str
    grade: str
    lesson_date: str
    start_time: str
    end_time: str
    total_amount: float
    status: str
    created_at: str


class OrderDetailResponse(BaseModel):
    order_id: int
    order_no: str
    parent_id: int
    teacher_id: int
    teacher_name: str = ""
    teacher_phone: str | None = None
    subject: str
    grade: str
    lesson_date: str
    start_time: str
    end_time: str
    duration: float
    unit_price: float
    total_amount: float
    commission_amount: float = 0.0
    settlement_amount: float = 0.0
    status: str
    pay_transaction_id: str | None = None
    paid_at: str | None = None
    teacher_accepted_at: str | None = None
    teacher_started_at: str | None = None
    teacher_completed_at: str | None = None
    parent_confirm_time: str | None = None
    completed_at: str | None = None
    cancelled_at: str | None = None
    cancel_reason: str | None = None
    created_at: str


class OrderActionRequest(BaseModel):
    """教师拒绝时的请求"""
    reason: str | None = Field(None, max_length=500)
