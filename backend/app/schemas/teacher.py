"""教师模块 Schemas"""

from pydantic import BaseModel, Field


# ---- 入驻申请 ----

class CertificateItem(BaseModel):
    cert_type: str = Field(..., pattern="^(student_card|other)$")
    image_url: str = Field(..., max_length=512)


class SubjectItem(BaseModel):
    subject: str = Field(..., max_length=32)
    grade_level: str = Field(..., max_length=32)
    unit_price: int = Field(default=0, ge=0)


class ScheduleItem(BaseModel):
    day_of_week: int = Field(..., ge=1, le=7)
    start_time: str = Field(..., description="格式 HH:MM")
    end_time: str = Field(..., description="格式 HH:MM")


class TeacherApplyRequest(BaseModel):
    """教师入驻申请"""
    real_name: str = Field(..., min_length=1, max_length=32)
    gender: str = Field(..., pattern="^(male|female)$")
    university: str = Field(default="河南大学", max_length=64)
    major: str = Field(..., min_length=1, max_length=64)
    grade: str = Field(..., min_length=1, max_length=16)
    bio: str | None = Field(None, max_length=500)
    min_price: int = Field(default=0, ge=0)
    teaching_regions: list[str] = Field(default_factory=list)
    subjects: list[SubjectItem] = Field(..., min_length=1)
    schedules: list[ScheduleItem] = Field(..., min_length=1)
    certificates: list[CertificateItem] = Field(default_factory=list)


class TeacherApplyResponse(BaseModel):
    teacher_id: int
    audit_status: str


# ---- 教师资料更新 ----

class TeacherProfileUpdateRequest(BaseModel):
    real_name: str | None = Field(None, max_length=32)
    gender: str | None = Field(None, pattern="^(male|female)$")
    major: str | None = Field(None, max_length=64)
    grade: str | None = Field(None, max_length=16)
    bio: str | None = Field(None, max_length=500)
    min_price: int | None = Field(None, ge=0)
    teaching_regions: list[str] | None = None
    is_available: bool | None = None


# ---- 教师列表项(公开) ----

class TeacherListItem(BaseModel):
    teacher_id: int
    nickname: str
    avatar_url: str | None = None
    university: str
    major: str
    grade: str
    subjects: list[str] = []
    min_price: int = 0
    avg_rating: float = 0.0
    review_count: int = 0
    is_available: bool = True
    teaching_regions: list[str] = []


# ---- 教师详情(公开) ----

class TeacherDetailResponse(BaseModel):
    teacher_id: int
    nickname: str
    avatar_url: str | None = None
    real_name: str
    gender: str
    university: str
    major: str
    grade: str
    bio: str | None = None
    min_price: int
    avg_rating: float = 0.0
    review_count: int = 0
    is_available: bool = True
    teaching_regions: list[str] = []
    certificates: list[dict] = []
    subjects: list[dict] = []
    schedules: list[dict] = []
    reviews: list[dict] = []
    contact_viewed: bool = False
    contact_expire_at: str | None = None
    is_favorited: bool = False


# ---- 联系方式查看 ----

class ContactViewResponse(BaseModel):
    phone: str
    wechat: str | None = None
    consumed_coins: int = 0
    balance_after: int = 0
    expire_at: str | None = None


# ---- 收入 ----

class IncomeOverview(BaseModel):
    balance: float = 0.0
    total_income: float = 0.0
    total_withdrawn: float = 0.0
    pending_settlement: float = 0.0


class IncomeRecord(BaseModel):
    order_id: int
    order_no: str
    amount: float
    created_at: str


class WithdrawRequest(BaseModel):
    amount: float = Field(..., gt=0)
