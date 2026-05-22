"""教师服务 — 入驻申请 / 资料管理 / 教学科目 / 排课 / 收入"""

import json
from datetime import datetime

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessError, NotFoundError
from app.models.teacher import Teacher
from app.models.teacher_certificate import TeacherCertificate
from app.models.teacher_subject import TeacherSubject
from app.models.teacher_schedule import TeacherSchedule
from app.models.order import Order
from app.models.user import User
from app.models.favorite import Favorite
from app.schemas.teacher import (
    TeacherApplyRequest,
    TeacherApplyResponse,
    TeacherListItem,
    TeacherDetailResponse,
    TeacherProfileUpdateRequest,
    IncomeOverview,
    IncomeRecord,
)


class TeacherService:
    """教师服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def apply(self, user: User, req: TeacherApplyRequest) -> TeacherApplyResponse:
        """教师入驻申请"""
        # 检查是否已申请
        existing = await self.db.execute(
            select(Teacher).where(Teacher.user_id == user.user_id)
        )
        if existing.scalar_one_or_none():
            raise BusinessError("您已提交过入驻申请")

        # 创建教师记录
        teacher = Teacher(
            user_id=user.user_id,
            real_name=req.real_name,
            gender=req.gender,
            university=req.university,
            major=req.major,
            grade=req.grade,
            bio=req.bio,
            min_price=req.min_price,
            teaching_regions=json.dumps(req.teaching_regions),
            audit_status="pending",
        )
        self.db.add(teacher)
        await self.db.flush()

        # 创建教学科目
        for subj in req.subjects:
            ts = TeacherSubject(
                teacher_id=teacher.teacher_id,
                subject=subj.subject,
                grade_level=subj.grade_level,
                unit_price=subj.unit_price,
            )
            self.db.add(ts)

        # 创建排课时间
        for sch in req.schedules:
            ts = TeacherSchedule(
                teacher_id=teacher.teacher_id,
                day_of_week=sch.day_of_week,
                start_time=sch.start_time,
                end_time=sch.end_time,
                status="available",
            )
            self.db.add(ts)

        # 创建证书
        for cert in req.certificates:
            tc = TeacherCertificate(
                teacher_id=teacher.teacher_id,
                cert_type=cert.cert_type,
                image_url=cert.image_url,
            )
            self.db.add(tc)

        return TeacherApplyResponse(
            teacher_id=teacher.teacher_id,
            audit_status=teacher.audit_status,
        )

    async def get_my_teacher(self, user: User) -> Teacher:
        """获取当前用户对应的教师记录"""
        result = await self.db.execute(
            select(Teacher).where(Teacher.user_id == user.user_id)
        )
        teacher = result.scalar_one_or_none()
        if not teacher:
            raise NotFoundError("请先完成教师入驻申请")
        return teacher

    async def update_profile(self, teacher: Teacher, req: TeacherProfileUpdateRequest) -> Teacher:
        """更新教师资料（审核通过后）"""
        if req.real_name is not None:
            teacher.real_name = req.real_name
        if req.gender is not None:
            teacher.gender = req.gender
        if req.major is not None:
            teacher.major = req.major
        if req.grade is not None:
            teacher.grade = req.grade
        if req.bio is not None:
            teacher.bio = req.bio
        if req.min_price is not None:
            teacher.min_price = req.min_price
        if req.teaching_regions is not None:
            teacher.teaching_regions = json.dumps(req.teaching_regions)
        if req.is_available is not None:
            teacher.is_available = 1 if req.is_available else 0

        await self.db.flush()
        return teacher

    async def get_teacher_list(
        self,
        keyword: str | None = None,
        subjects: str | None = None,
        grade_level: str | None = None,
        region: str | None = None,
        gender: str | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
        sort: str = "rating",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[TeacherListItem], int]:
        """教师列表搜索"""
        query = (
            select(Teacher)
            .join(User, Teacher.user_id == User.user_id)
            .where(Teacher.audit_status == "approved", Teacher.is_available == 1)
        )

        if subjects:
            subj_list = [s.strip() for s in subjects.split(",")]
            query = query.join(
                TeacherSubject,
                Teacher.teacher_id == TeacherSubject.teacher_id,
            ).where(TeacherSubject.subject.in_(subj_list))

        if grade_level:
            query = query.where(TeacherSubject.grade_level == grade_level)

        if region:
            query = query.where(Teacher.teaching_regions.contains(region))

        if gender:
            query = query.where(Teacher.gender == gender)

        if min_price is not None:
            query = query.where(Teacher.min_price >= min_price)
        if max_price is not None:
            query = query.where(Teacher.min_price <= max_price)

        if keyword:
            query = query.where(
                (User.nickname.contains(keyword)) | (Teacher.major.contains(keyword))
            )

        # 排序
        if sort == "price_asc":
            query = query.order_by(Teacher.min_price.asc())
        elif sort == "price_desc":
            query = query.order_by(Teacher.min_price.desc())
        else:
            query = query.order_by(Teacher.avg_rating.desc())

        # 去重 (因 join subjects 可能产生重复)
        query = query.distinct()

        # 计数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # 分页
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        teachers = result.scalars().all()

        items = []
        for t in teachers:
            items.append(TeacherListItem(
                teacher_id=t.teacher_id,
                nickname=t.user.nickname or "教师",
                avatar_url=t.user.avatar_url,
                university=t.university,
                major=t.major,
                grade=t.grade,
                subjects=[s.subject for s in t.subjects],
                min_price=t.min_price,
                avg_rating=float(t.avg_rating),
                review_count=t.review_count,
                is_available=t.is_available == 1,
                teaching_regions=json.loads(t.teaching_regions or "[]"),
            ))

        return items, total

    async def get_teacher_detail(
        self, teacher_id: int, current_user: User | None = None
    ) -> TeacherDetailResponse:
        """教师详情"""
        result = await self.db.execute(
            select(Teacher).where(Teacher.teacher_id == teacher_id, Teacher.audit_status == "approved")
        )
        teacher = result.scalar_one_or_none()
        if not teacher:
            raise NotFoundError("教师不存在")

        is_favorited = False
        if current_user:
            fav_result = await self.db.execute(
                select(Favorite).where(
                    Favorite.parent_id == current_user.user_id,
                    Favorite.teacher_id == teacher_id,
                )
            )
            is_favorited = fav_result.scalar_one_or_none() is not None

        return TeacherDetailResponse(
            teacher_id=teacher.teacher_id,
            nickname=teacher.user.nickname or "教师",
            avatar_url=teacher.user.avatar_url,
            real_name=teacher.real_name,
            gender=teacher.gender,
            university=teacher.university,
            major=teacher.major,
            grade=teacher.grade,
            bio=teacher.bio,
            min_price=teacher.min_price,
            avg_rating=float(teacher.avg_rating),
            review_count=teacher.review_count,
            is_available=teacher.is_available == 1,
            teaching_regions=json.loads(teacher.teaching_regions or "[]"),
            certificates=[{"cert_type": c.cert_type, "image_url": c.image_url} for c in teacher.certificates],
            subjects=[{"subject": s.subject, "grade_level": s.grade_level, "unit_price": s.unit_price} for s in teacher.subjects],
            schedules=[{"day_of_week": s.day_of_week, "start_time": str(s.start_time), "end_time": str(s.end_time), "status": s.status} for s in teacher.schedules],
            reviews=[],
            is_favorited=is_favorited,
        )

    async def get_income(self, teacher: Teacher) -> IncomeOverview:
        """教师收入概览"""
        # 已完成订单的结算金额
        result = await self.db.execute(
            select(
                func.coalesce(func.sum(Order.settlement_amount), 0),
                func.count(Order.order_id),
            ).where(
                Order.teacher_id == teacher.teacher_id,
                Order.status == "completed",
            )
        )
        total_settlement, completed_count = result.one()
        total_settlement = float(total_settlement or 0)

        # 待结算
        pending_result = await self.db.execute(
            select(func.coalesce(func.sum(Order.settlement_amount), 0)).where(
                Order.teacher_id == teacher.teacher_id,
                Order.status.in_(["pending_settlement", "in_progress", "pending_trial", "pending_confirm"]),
            )
        )
        pending = float(pending_result.scalar() or 0)

        return IncomeOverview(
            balance=total_settlement,
            total_income=total_settlement,
            total_withdrawn=0,
            pending_settlement=pending,
        )

    async def get_income_records(self, teacher: Teacher, page: int, page_size: int) -> tuple[list[IncomeRecord], int]:
        """教师收入明细"""
        count_result = await self.db.execute(
            select(func.count(Order.order_id)).where(
                Order.teacher_id == teacher.teacher_id,
                Order.status == "completed",
            )
        )
        total = count_result.scalar() or 0

        result = await self.db.execute(
            select(Order)
            .where(Order.teacher_id == teacher.teacher_id, Order.status == "completed")
            .order_by(Order.completed_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        orders = result.scalars().all()

        records = [
            IncomeRecord(
                order_id=o.order_id,
                order_no=o.order_no,
                amount=float(o.settlement_amount),
                created_at=str(o.completed_at) if o.completed_at else str(o.created_at),
            )
            for o in orders
        ]
        return records, total
