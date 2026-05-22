"""需求发布 API"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.deps.auth import require_parent
from app.api.deps.pagination import pagination
from app.models.user import User
from app.models.parent_demand import ParentDemand
from app.schemas.demand import CreateDemandRequest, UpdateDemandRequest
from app.schemas.common import APIResponse, PaginationParams, paginate

router = APIRouter(prefix="/demands", tags=["需求"])


@router.post("", response_model=APIResponse)
async def create_demand(
    req: CreateDemandRequest,
    user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_db),
):
    """发布需求"""
    demand = ParentDemand(
        parent_id=user.user_id,
        subjects=req.subjects,
        grade=req.grade,
        address=req.address,
        address_detail=req.address_detail,
        budget_min=req.budget_min,
        budget_max=req.budget_max,
        frequency=req.frequency,
        expect_time=req.expect_time,
        student_note=req.student_note,
        teacher_requirement=req.teacher_requirement,
        status="open",
    )
    db.add(demand)
    await db.flush()
    return APIResponse.success(data={"demand_id": demand.demand_id})


@router.get("", response_model=APIResponse)
async def list_demands(
    user: User = Depends(require_parent),
    pagination: PaginationParams = Depends(pagination),
    db: AsyncSession = Depends(get_db),
):
    """我的需求列表"""
    from sqlalchemy import func

    query = select(ParentDemand).where(ParentDemand.parent_id == user.user_id)
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(ParentDemand.created_at.desc()).offset(
        (pagination.page - 1) * pagination.page_size
    ).limit(pagination.page_size)
    result = await db.execute(query)
    demands = result.scalars().all()

    items = [
        {
            "demand_id": d.demand_id,
            "subjects": d.subjects,
            "grade": d.grade,
            "address": d.address,
            "budget_min": d.budget_min,
            "budget_max": d.budget_max,
            "status": d.status,
            "created_at": str(d.created_at),
        }
        for d in demands
    ]
    return APIResponse.success(data=paginate(items, total, pagination.page, pagination.page_size))


@router.get("/{demand_id}", response_model=APIResponse)
async def get_demand(
    demand_id: int,
    user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_db),
):
    """需求详情"""
    result = await db.execute(select(ParentDemand).where(ParentDemand.demand_id == demand_id))
    demand = result.scalar_one_or_none()
    if not demand:
        return APIResponse.error(1004, "需求不存在")
    if demand.parent_id != user.user_id:
        return APIResponse.error(1003, "无权查看")

    return APIResponse.success(data={
        "demand_id": demand.demand_id,
        "subjects": demand.subjects,
        "grade": demand.grade,
        "address": demand.address,
        "address_detail": demand.address_detail,
        "budget_min": demand.budget_min,
        "budget_max": demand.budget_max,
        "frequency": demand.frequency,
        "expect_time": demand.expect_time,
        "student_note": demand.student_note,
        "teacher_requirement": demand.teacher_requirement,
        "status": demand.status,
        "created_at": str(demand.created_at),
    })


@router.put("/{demand_id}", response_model=APIResponse)
async def update_demand(
    demand_id: int,
    req: UpdateDemandRequest,
    user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_db),
):
    """修改需求"""
    result = await db.execute(select(ParentDemand).where(ParentDemand.demand_id == demand_id))
    demand = result.scalar_one_or_none()
    if not demand:
        return APIResponse.error(1004, "需求不存在")
    if demand.parent_id != user.user_id:
        return APIResponse.error(1003, "无权修改")

    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(demand, key, value)
    await db.flush()

    return APIResponse.success(message="更新成功")


@router.delete("/{demand_id}", response_model=APIResponse)
async def close_demand(
    demand_id: int,
    user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_db),
):
    """关闭需求"""
    result = await db.execute(select(ParentDemand).where(ParentDemand.demand_id == demand_id))
    demand = result.scalar_one_or_none()
    if not demand:
        return APIResponse.error(1004, "需求不存在")
    if demand.parent_id != user.user_id:
        return APIResponse.error(1003, "无权操作")

    demand.status = "closed"
    await db.flush()
    return APIResponse.success(message="已关闭")
