"""管理员 API — 教师审核 + 系统配置"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps.auth import require_admin
from app.api.deps.pagination import pagination
from app.models.user import User
from app.models.teacher import Teacher
from app.models.system_config import SystemConfig
from app.schemas.common import APIResponse, PaginationParams, paginate

router = APIRouter(prefix="/admin", tags=["管理员"])


# ── Pydantic schemas ───────────────────────────────────────────────

class RejectRequest(BaseModel):
    reason: str | None = None


class ConfigUpdateRequest(BaseModel):
    configs: dict[str, str]


# ── Teacher audit endpoints ────────────────────────────────────────

@router.get("/teachers", response_model=APIResponse)
async def list_teachers_for_audit(
    audit_status: str = Query("pending", description="审核状态: pending/approved/rejected"),
    pagination: PaginationParams = Depends(pagination),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """管理员查看教师列表（按审核状态筛选）"""
    base_query = (
        select(Teacher)
        .join(User, Teacher.user_id == User.user_id)
        .where(Teacher.audit_status == audit_status)
    )

    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = base_query.offset(
        (pagination.page - 1) * pagination.page_size
    ).limit(pagination.page_size).order_by(Teacher.created_at.desc())

    result = await db.execute(query)
    teachers = result.scalars().all()

    items = [
        {
            "teacher_id": t.teacher_id,
            "real_name": t.real_name,
            "gender": t.gender,
            "university": t.university,
            "major": t.major,
            "grade": t.grade,
            "audit_status": t.audit_status,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "nickname": t.user.nickname,
            "phone": t.user.phone,
        }
        for t in teachers
    ]

    return APIResponse.success(
        data=paginate(items, total, pagination.page, pagination.page_size)
    )


@router.post("/teachers/{teacher_id}/approve", response_model=APIResponse)
async def approve_teacher(
    teacher_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """审核通过教师"""
    result = await db.execute(select(Teacher).where(Teacher.teacher_id == teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        return APIResponse.error(1004, "教师不存在")
    if teacher.audit_status != "pending":
        return APIResponse.error(1005, f"教师当前状态为「{teacher.audit_status}」，无法审核")

    teacher.audit_status = "approved"
    teacher.audit_reason = None
    teacher.audited_at = datetime.now()
    await db.commit()

    return APIResponse.success(message="审核通过")


@router.post("/teachers/{teacher_id}/reject", response_model=APIResponse)
async def reject_teacher(
    teacher_id: int,
    req: RejectRequest,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """驳回教师申请"""
    result = await db.execute(select(Teacher).where(Teacher.teacher_id == teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        return APIResponse.error(1004, "教师不存在")
    if teacher.audit_status != "pending":
        return APIResponse.error(1005, f"教师当前状态为「{teacher.audit_status}」，无法审核")

    teacher.audit_status = "rejected"
    teacher.audit_reason = req.reason
    teacher.audited_at = datetime.now()
    await db.commit()

    return APIResponse.success(message="已驳回", data={"reason": req.reason})


# ── System config endpoints ────────────────────────────────────────

@router.get("/config", response_model=APIResponse)
async def get_system_configs(
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """获取所有系统配置"""
    result = await db.execute(select(SystemConfig))
    configs = result.scalars().all()

    items = [
        {
            "config_key": c.config_key,
            "config_value": c.config_value,
            "description": c.description,
        }
        for c in configs
    ]

    return APIResponse.success(data=items)


@router.put("/config", response_model=APIResponse)
async def update_system_configs(
    req: ConfigUpdateRequest,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """批量更新系统配置（upsert）"""
    updated = []

    for key, value in req.configs.items():
        result = await db.execute(
            select(SystemConfig).where(SystemConfig.config_key == key)
        )
        config = result.scalar_one_or_none()

        if config:
            config.config_value = value
            config.updated_at = datetime.now()
        else:
            config = SystemConfig(config_key=key, config_value=value, description=None)
            db.add(config)

        updated.append({"config_key": key, "config_value": value})

    await db.commit()

    return APIResponse.success(data=updated, message="配置已更新")
