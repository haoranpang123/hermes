"""需求模块 Schemas"""

from pydantic import BaseModel, Field


class CreateDemandRequest(BaseModel):
    subjects: str = Field(..., max_length=256)
    grade: str = Field(..., max_length=32)
    address: str = Field(..., max_length=256)
    address_detail: str | None = Field(None, max_length=256)
    budget_min: int | None = Field(None, ge=0)
    budget_max: int | None = Field(None, ge=0)
    frequency: str = Field(..., max_length=16)
    expect_time: str | None = Field(None, max_length=256)
    student_note: str | None = None
    teacher_requirement: str | None = None


class UpdateDemandRequest(BaseModel):
    subjects: str | None = Field(None, max_length=256)
    grade: str | None = Field(None, max_length=32)
    address: str | None = Field(None, max_length=256)
    address_detail: str | None = Field(None, max_length=256)
    budget_min: int | None = Field(None, ge=0)
    budget_max: int | None = Field(None, ge=0)
    frequency: str | None = Field(None, max_length=16)
    expect_time: str | None = Field(None, max_length=256)
    student_note: str | None = None
    teacher_requirement: str | None = None


class DemandItem(BaseModel):
    demand_id: int
    subjects: str
    grade: str
    address: str
    budget_min: int | None = None
    budget_max: int | None = None
    status: str
    created_at: str
