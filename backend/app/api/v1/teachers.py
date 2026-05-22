"""教师浏览 API (公开 + 家长端) — 教师列表 / 详情 / 收藏 / 联系方式"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps.auth import get_current_user, require_parent
from app.api.deps.pagination import pagination
from app.services.teacher_service import TeacherService
from app.services.wallet_service import WalletService
from app.models.user import User
from app.models.favorite import Favorite
from app.schemas.teacher import ContactViewResponse, TeacherListItem, TeacherDetailResponse
from app.schemas.common import APIResponse, PaginatedData, PaginationParams, paginate

router = APIRouter(prefix="/teachers", tags=["教师浏览"])


@router.get("", response_model=APIResponse)
async def list_teachers(
    keyword: str | None = Query(None),
    subjects: str | None = Query(None),
    grade_level: str | None = Query(None),
    region: str | None = Query(None),
    gender: str | None = Query(None),
    min_price: int | None = Query(None),
    max_price: int | None = Query(None),
    sort: str = Query("rating"),
    pagination: PaginationParams = Depends(pagination),
    db: AsyncSession = Depends(get_db),
):
    """教师列表 (公开)"""
    svc = TeacherService(db)
    items, total = await svc.get_teacher_list(
        keyword=keyword,
        subjects=subjects,
        grade_level=grade_level,
        region=region,
        gender=gender,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return APIResponse.success(data=paginate(items, total, pagination.page, pagination.page_size))


@router.get("/{teacher_id}", response_model=APIResponse[TeacherDetailResponse])
async def get_teacher_detail(
    teacher_id: int,
    user: User | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """教师详情 (公开，但登录后展示更多信息)"""
    svc = TeacherService(db)
    result = await svc.get_teacher_detail(teacher_id, current_user=user)
    return APIResponse.success(data=result)


@router.post("/{teacher_id}/contact", response_model=APIResponse[ContactViewResponse])
async def view_teacher_contact(
    teacher_id: int,
    user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_db),
):
    """查看教师联系方式 (消耗虚拟币)"""
    from app.config import get_settings
    settings = get_settings()

    # 查找教师
    from app.models.teacher import Teacher
    from sqlalchemy import select
    result = await db.execute(
        select(Teacher).where(Teacher.teacher_id == teacher_id, Teacher.audit_status == "approved")
    )
    teacher = result.scalar_one_or_none()
    if not teacher:
        return APIResponse.error(1004, "教师不存在")

    # 消耗虚拟币
    wallet_svc = WalletService(db)
    consume_result = await wallet_svc.consume_coins(
        user=user,
        amount=settings.CONTACT_COIN_PRICE,
        description=f"查看{teacher.real_name}联系方式",
        ref_id=teacher_id,
        ref_type="teacher",
    )

    return APIResponse.success(data=ContactViewResponse(
        phone=teacher.user.phone or f"138****{teacher.teacher_id:04d}",
        wechat=None,
        consumed_coins=consume_result["consumed_coins"],
        balance_after=consume_result["balance_after"],
        expire_at=None,
    ))


@router.post("/{teacher_id}/favorite", response_model=APIResponse)
async def favorite_teacher(
    teacher_id: int,
    user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_db),
):
    """收藏教师"""
    from sqlalchemy import select
    existing = await db.execute(
        select(Favorite).where(Favorite.parent_id == user.user_id, Favorite.teacher_id == teacher_id)
    )
    if existing.scalar_one_or_none():
        return APIResponse.success(message="已收藏")

    fav = Favorite(parent_id=user.user_id, teacher_id=teacher_id)
    db.add(fav)
    return APIResponse.success(message="收藏成功")


@router.delete("/{teacher_id}/favorite", response_model=APIResponse)
async def unfavorite_teacher(
    teacher_id: int,
    user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_db),
):
    """取消收藏"""
    from sqlalchemy import select, delete
    await db.execute(
        delete(Favorite).where(Favorite.parent_id == user.user_id, Favorite.teacher_id == teacher_id)
    )
    return APIResponse.success(message="已取消收藏")


@router.get("/favorites", response_model=APIResponse)
async def get_favorites(
    user: User = Depends(require_parent),
    pagination: PaginationParams = Depends(pagination),
    db: AsyncSession = Depends(get_db),
):
    """我的收藏列表"""
    svc = TeacherService(db)
    # Simplified - re-use get_teacher_list if needed
    from sqlalchemy import select, func
    from app.models.teacher import Teacher as TeacherModel
    from app.models.user import User as UserModel

    fav_query = (
        select(TeacherModel)
        .join(Favorite, Favorite.teacher_id == TeacherModel.teacher_id)
        .join(UserModel, TeacherModel.user_id == UserModel.user_id)
        .where(Favorite.parent_id == user.user_id)
    )

    count_query = select(func.count()).select_from(fav_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    fav_query = fav_query.offset((pagination.page - 1) * pagination.page_size).limit(pagination.page_size)
    result = await db.execute(fav_query)
    teachers = result.scalars().all()

    import json
    items = [
        {
            "teacher_id": t.teacher_id,
            "nickname": t.user.nickname,
            "university": t.university,
            "min_price": t.min_price,
            "avg_rating": float(t.avg_rating),
        }
        for t in teachers
    ]

    return APIResponse.success(data=paginate(items, total, pagination.page, pagination.page_size))
