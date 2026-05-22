"""教师入驻与管理 API"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps.auth import get_current_user, require_teacher
from app.api.deps.pagination import pagination
from app.services.teacher_service import TeacherService
from app.models.user import User
from app.models.teacher import Teacher
from app.schemas.teacher import (
    TeacherApplyRequest,
    TeacherApplyResponse,
    TeacherProfileUpdateRequest,
    IncomeOverview,
    WithdrawRequest,
)
from app.schemas.common import APIResponse, PaginationParams, paginate

router = APIRouter(prefix="/teacher", tags=["教师入驻"])


@router.post("/apply", response_model=APIResponse[TeacherApplyResponse])
async def apply(
    req: TeacherApplyRequest,
    user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    """提交入驻申请"""
    svc = TeacherService(db)
    result = await svc.apply(user, req)
    return APIResponse.success(data=result)


@router.get("/status", response_model=APIResponse)
async def get_status(
    user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    """查询审核状态"""
    svc = TeacherService(db)
    teacher = await svc.get_my_teacher(user)
    return APIResponse.success(data={
        "teacher_id": teacher.teacher_id,
        "audit_status": teacher.audit_status,
        "audit_reason": teacher.audit_reason,
        "audited_at": str(teacher.audited_at) if teacher.audited_at else None,
        "created_at": str(teacher.created_at),
    })


@router.get("/profile", response_model=APIResponse)
async def get_profile(
    user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    """获取教师完整资料"""
    svc = TeacherService(db)
    teacher = await svc.get_my_teacher(user)
    import json
    return APIResponse.success(data={
        "teacher_id": teacher.teacher_id,
        "real_name": teacher.real_name,
        "gender": teacher.gender,
        "university": teacher.university,
        "major": teacher.major,
        "grade": teacher.grade,
        "bio": teacher.bio,
        "min_price": teacher.min_price,
        "teaching_regions": json.loads(teacher.teaching_regions or "[]"),
        "avg_rating": float(teacher.avg_rating),
        "review_count": teacher.review_count,
        "is_available": teacher.is_available == 1,
        "audit_status": teacher.audit_status,
        "subjects": [{"subject": s.subject, "grade_level": s.grade_level, "unit_price": s.unit_price} for s in teacher.subjects],
        "schedules": [{"day_of_week": s.day_of_week, "start_time": str(s.start_time), "end_time": str(s.end_time)} for s in teacher.schedules],
        "certificates": [{"cert_type": c.cert_type, "image_url": c.image_url} for c in teacher.certificates],
    })


@router.put("/profile", response_model=APIResponse)
async def update_profile(
    req: TeacherProfileUpdateRequest,
    user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    """修改教师资料"""
    svc = TeacherService(db)
    teacher = await svc.get_my_teacher(user)
    await svc.update_profile(teacher, req)
    return APIResponse.success(message="更新成功")


@router.get("/income", response_model=APIResponse[IncomeOverview])
async def get_income(
    user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    """收入概览"""
    svc = TeacherService(db)
    teacher = await svc.get_my_teacher(user)
    result = await svc.get_income(teacher)
    return APIResponse.success(data=result)


@router.get("/income/records", response_model=APIResponse)
async def get_income_records(
    user: User = Depends(require_teacher),
    pagination: PaginationParams = Depends(pagination),
    db: AsyncSession = Depends(get_db),
):
    """收入明细"""
    svc = TeacherService(db)
    teacher = await svc.get_my_teacher(user)
    items, total = await svc.get_income_records(teacher, pagination.page, pagination.page_size)
    return APIResponse.success(data=paginate(items, total, pagination.page, pagination.page_size))


@router.post("/withdraw", response_model=APIResponse)
async def withdraw(
    req: WithdrawRequest,
    user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    """申请提现"""
    # MVP: 暂不实现完整提现逻辑，记录需求
    return APIResponse.success(message="提现申请已提交（MVP暂需管理员审核）")
