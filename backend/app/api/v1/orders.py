"""订单 API"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps.auth import get_current_user, require_parent, require_teacher
from app.api.deps.pagination import pagination
from app.services.order_service import OrderService
from app.services.teacher_service import TeacherService
from app.models.user import User
from app.schemas.order import (
    CreateOrderRequest,
    CreateOrderResponse,
    OrderDetailResponse,
    OrderActionRequest,
)
from app.schemas.common import APIResponse, PaginationParams, paginate

router = APIRouter(prefix="/orders", tags=["订单"])


@router.post("", response_model=APIResponse[CreateOrderResponse])
async def create_order(
    req: CreateOrderRequest,
    user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_db),
):
    """家长创建订单"""
    svc = OrderService(db)
    result = await svc.create_order(user, req)
    return APIResponse.success(data=result)


@router.get("", response_model=APIResponse)
async def list_orders(
    status: str | None = Query(None),
    user: User = Depends(get_current_user),
    pagination: PaginationParams = Depends(pagination),
    db: AsyncSession = Depends(get_db),
):
    """订单列表 (按角色)"""
    svc = OrderService(db)
    items, total = await svc.get_order_list(user, status, pagination.page, pagination.page_size)
    return APIResponse.success(data=paginate(items, total, pagination.page, pagination.page_size))


@router.get("/{order_id}", response_model=APIResponse[OrderDetailResponse])
async def get_order_detail(
    order_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """订单详情"""
    svc = OrderService(db)
    result = await svc.get_order_detail(order_id, user)
    return APIResponse.success(data=result)


@router.post("/{order_id}/accept", response_model=APIResponse)
async def accept_order(
    order_id: int,
    user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    """教师确认接单"""
    teacher_svc = TeacherService(db)
    teacher = await teacher_svc.get_my_teacher(user)
    svc = OrderService(db)
    result = await svc.teacher_accept(order_id, teacher)
    return APIResponse.success(data=result)


@router.post("/{order_id}/reject", response_model=APIResponse)
async def reject_order(
    order_id: int,
    req: OrderActionRequest,
    user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    """教师拒绝接单"""
    teacher_svc = TeacherService(db)
    teacher = await teacher_svc.get_my_teacher(user)
    svc = OrderService(db)
    result = await svc.teacher_reject(order_id, teacher, req.reason)
    return APIResponse.success(data=result)


@router.post("/{order_id}/start", response_model=APIResponse)
async def start_order(
    order_id: int,
    user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    """教师标记已上课"""
    teacher_svc = TeacherService(db)
    teacher = await teacher_svc.get_my_teacher(user)
    svc = OrderService(db)
    result = await svc.teacher_start(order_id, teacher)
    return APIResponse.success(data=result)


@router.post("/{order_id}/complete", response_model=APIResponse)
async def complete_order(
    order_id: int,
    user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    """教师标记完成"""
    teacher_svc = TeacherService(db)
    teacher = await teacher_svc.get_my_teacher(user)
    svc = OrderService(db)
    result = await svc.teacher_complete(order_id, teacher)
    return APIResponse.success(data=result)


@router.post("/{order_id}/confirm", response_model=APIResponse)
async def confirm_order(
    order_id: int,
    user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_db),
):
    """家长确认完成 → 结算"""
    svc = OrderService(db)
    result = await svc.parent_confirm(order_id, user)
    return APIResponse.success(data=result)
