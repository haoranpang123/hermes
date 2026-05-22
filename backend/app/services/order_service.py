"""订单服务 — 创建 / 支付回调 / 状态流转"""

import json
from datetime import date, datetime, timedelta, time
from decimal import Decimal

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.exceptions import BusinessError, NotFoundError, ValidationError
from app.models.order import Order
from app.models.teacher import Teacher
from app.models.teacher_subject import TeacherSubject
from app.models.user import User
from app.schemas.order import CreateOrderRequest, CreateOrderResponse, OrderListItem, OrderDetailResponse

settings = get_settings()


def generate_order_no() -> str:
    """生成订单号: HD + 日期 + 5位随机"""
    import random
    today = datetime.now().strftime("%Y%m%d")
    rand = str(random.randint(10000, 99999))
    return f"HD{today}{rand}"


class OrderService:
    """订单服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(self, parent: User, req: CreateOrderRequest) -> CreateOrderResponse:
        """家长创建订单"""
        # 查找教师
        result = await self.db.execute(
            select(Teacher).where(Teacher.teacher_id == req.teacher_id, Teacher.audit_status == "approved")
        )
        teacher = result.scalar_one_or_none()
        if not teacher:
            raise NotFoundError("教师不存在或未通过审核")
        if teacher.is_available == 0:
            raise BusinessError("该教师当前暂不可预约")

        # 计算价格
        unit_price = Decimal(str(teacher.min_price))
        subj_result = await self.db.execute(
            select(TeacherSubject).where(
                TeacherSubject.teacher_id == teacher.teacher_id,
                TeacherSubject.subject == req.subject,
            )
        )
        subj = subj_result.scalar_one_or_none()
        if subj and subj.unit_price > 0:
            unit_price = Decimal(str(subj.unit_price))

        # 计算时长
        lesson_date_obj = date.fromisoformat(req.lesson_date)
        start_time_obj = time.fromisoformat(req.start_time)
        end_time_obj = time.fromisoformat(req.end_time)

        start_min = start_time_obj.hour * 60 + start_time_obj.minute
        end_min = end_time_obj.hour * 60 + end_time_obj.minute
        if end_min <= start_min:
            raise ValidationError("结束时间必须晚于开始时间")

        duration = Decimal(str(round((end_min - start_min) / 60.0, 1)))
        total_amount = duration * unit_price
        commission_amount = total_amount * Decimal(str(settings.DEFAULT_COMMISSION_RATE))
        settlement_amount = total_amount - commission_amount

        # 创建订单
        order = Order(
            order_no=generate_order_no(),
            parent_id=parent.user_id,
            teacher_id=teacher.teacher_id,
            subject=req.subject,
            grade=req.grade,
            lesson_date=lesson_date_obj,
            start_time=start_time_obj,
            end_time=end_time_obj,
            duration=duration,
            unit_price=unit_price,
            total_amount=total_amount,
            commission_rate=Decimal(str(settings.DEFAULT_COMMISSION_RATE)),
            commission_amount=commission_amount,
            settlement_amount=settlement_amount,
            status="pending_confirm",
        )
        self.db.add(order)
        await self.db.flush()

        # MVP: 微信支付参数为 mock (生产环境需调用微信统一下单)
        wechat_pay_params = {
            "appId": settings.WX_APP_ID or "mock_appid",
            "timeStamp": str(int(datetime.now().timestamp())),
            "nonceStr": "mock_nonce",
            "package": f"prepay_id=mock_{order.order_no}",
            "signType": "RSA",
            "paySign": "mock_sign",
        }

        return CreateOrderResponse(
            order_id=order.order_id,
            order_no=order.order_no,
            total_amount=float(total_amount),
            wechat_pay_params=wechat_pay_params,
        )

    async def get_order_list(
        self, user: User, status: str | None = None, page: int = 1, page_size: int = 20
    ) -> tuple[list[OrderListItem], int]:
        """订单列表(按角色)"""
        if user.role == "parent":
            query = select(Order).where(Order.parent_id == user.user_id)
        elif user.role == "teacher":
            t_result = await self.db.execute(select(Teacher).where(Teacher.user_id == user.user_id))
            teacher = t_result.scalar_one_or_none()
            if not teacher:
                raise NotFoundError("教师信息不存在")
            query = select(Order).where(Order.teacher_id == teacher.teacher_id)
        else:
            raise BusinessError("无效角色")

        if status:
            query = query.where(Order.status == status)

        # 计数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # 分页
        query = query.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        orders = result.scalars().all()

        items = []
        for o in orders:
            teacher_name = o.teacher.real_name if o.teacher else ""
            items.append(OrderListItem(
                order_id=o.order_id,
                order_no=o.order_no,
                teacher_id=o.teacher_id,
                parent_id=o.parent_id,
                teacher_name=teacher_name,
                subject=o.subject,
                grade=o.grade,
                lesson_date=str(o.lesson_date),
                start_time=str(o.start_time),
                end_time=str(o.end_time),
                total_amount=float(o.total_amount),
                status=o.status,
                created_at=str(o.created_at),
            ))

        return items, total

    async def get_order_detail(self, order_id: int, user: User) -> OrderDetailResponse:
        """订单详情"""
        result = await self.db.execute(select(Order).where(Order.order_id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            raise NotFoundError("订单不存在")

        # 权限检查
        if user.role == "parent" and order.parent_id != user.user_id:
            raise BusinessError("无权查看")
        if user.role == "teacher":
            t_result = await self.db.execute(select(Teacher).where(Teacher.user_id == user.user_id))
            teacher = t_result.scalar_one_or_none()
            if not teacher or order.teacher_id != teacher.teacher_id:
                raise BusinessError("无权查看")

        teacher_name = order.teacher.real_name if order.teacher else ""

        return OrderDetailResponse(
            order_id=order.order_id,
            order_no=order.order_no,
            parent_id=order.parent_id,
            teacher_id=order.teacher_id,
            teacher_name=teacher_name,
            teacher_phone=order.teacher.user.phone if order.teacher and order.status in ("completed", "pending_trial") else None,
            subject=order.subject,
            grade=order.grade,
            lesson_date=str(order.lesson_date),
            start_time=str(order.start_time),
            end_time=str(order.end_time),
            duration=float(order.duration),
            unit_price=float(order.unit_price),
            total_amount=float(order.total_amount),
            commission_amount=float(order.commission_amount),
            settlement_amount=float(order.settlement_amount),
            status=order.status,
            pay_transaction_id=order.pay_transaction_id,
            paid_at=str(order.paid_at) if order.paid_at else None,
            teacher_accepted_at=str(order.teacher_accepted_at) if order.teacher_accepted_at else None,
            teacher_started_at=str(order.teacher_started_at) if order.teacher_started_at else None,
            teacher_completed_at=str(order.teacher_completed_at) if order.teacher_completed_at else None,
            parent_confirm_time=str(order.parent_confirm_time) if order.parent_confirm_time else None,
            completed_at=str(order.completed_at) if order.completed_at else None,
            cancelled_at=str(order.cancelled_at) if order.cancelled_at else None,
            cancel_reason=order.cancel_reason,
            created_at=str(order.created_at),
        )

    async def teacher_accept(self, order_id: int, teacher: Teacher) -> dict:
        """教师确认接单"""
        result = await self.db.execute(select(Order).where(Order.order_id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            raise NotFoundError("订单不存在")
        if order.teacher_id != teacher.teacher_id:
            raise BusinessError("无权操作该订单")
        if order.status != "pending_confirm":
            raise BusinessError(f"订单状态为 {order.status}，无法接单")

        order.status = "pending_trial"
        order.teacher_accepted_at = datetime.now()
        await self.db.flush()

        return {"order_id": order.order_id, "status": order.status, "accepted_at": str(order.teacher_accepted_at)}

    async def teacher_reject(self, order_id: int, teacher: Teacher, reason: str | None = None) -> dict:
        """教师拒绝接单"""
        result = await self.db.execute(select(Order).where(Order.order_id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            raise NotFoundError("订单不存在")
        if order.teacher_id != teacher.teacher_id:
            raise BusinessError("无权操作该订单")
        if order.status != "pending_confirm":
            raise BusinessError(f"订单状态为 {order.status}，无法拒绝")

        order.status = "cancelled"
        order.cancelled_at = datetime.now()
        order.cancel_reason = reason or "教师拒绝接单"
        await self.db.flush()

        return {"order_id": order.order_id, "status": order.status}

    async def teacher_start(self, order_id: int, teacher: Teacher) -> dict:
        """教师标记已上课"""
        result = await self.db.execute(select(Order).where(Order.order_id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            raise NotFoundError("订单不存在")
        if order.teacher_id != teacher.teacher_id:
            raise BusinessError("无权操作该订单")
        if order.status != "pending_trial":
            raise BusinessError(f"订单状态为 {order.status}，无法标记上课")

        order.status = "in_progress"
        order.teacher_started_at = datetime.now()
        await self.db.flush()

        return {"order_id": order.order_id, "status": order.status}

    async def teacher_complete(self, order_id: int, teacher: Teacher) -> dict:
        """教师标记完成"""
        result = await self.db.execute(select(Order).where(Order.order_id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            raise NotFoundError("订单不存在")
        if order.teacher_id != teacher.teacher_id:
            raise BusinessError("无权操作该订单")
        if order.status != "in_progress":
            raise BusinessError(f"订单状态为 {order.status}，无法标记完成")

        order.status = "pending_settlement"
        order.teacher_completed_at = datetime.now()
        order.auto_confirm_deadline = datetime.now() + timedelta(hours=settings.AUTO_CONFIRM_HOURS)
        await self.db.flush()

        return {"order_id": order.order_id, "status": order.status, "auto_confirm_deadline": str(order.auto_confirm_deadline)}

    async def parent_confirm(self, order_id: int, parent: User) -> dict:
        """家长确认完成 → 结算"""
        result = await self.db.execute(select(Order).where(Order.order_id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            raise NotFoundError("订单不存在")
        if order.parent_id != parent.user_id:
            raise BusinessError("无权操作该订单")
        if order.status != "pending_settlement":
            raise BusinessError(f"订单状态为 {order.status}，无法确认")

        order.status = "completed"
        order.parent_confirm_time = datetime.now()
        order.completed_at = datetime.now()
        await self.db.flush()

        return {
            "order_id": order.order_id,
            "status": order.status,
            "total_amount": float(order.total_amount),
            "commission_amount": float(order.commission_amount),
            "settlement_amount": float(order.settlement_amount),
        }
