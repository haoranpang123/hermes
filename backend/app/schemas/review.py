"""评价模块 Schemas"""

from pydantic import BaseModel, Field


class CreateReviewRequest(BaseModel):
    order_id: int = Field(..., gt=0)
    teaching_ability: int = Field(..., ge=1, le=5)
    communication: int = Field(..., ge=1, le=5)
    punctuality: int = Field(..., ge=1, le=5)
    content: str | None = Field(None, max_length=500)


class ReviewItem(BaseModel):
    review_id: int
    parent_nickname: str
    teaching_ability: int
    communication: int
    punctuality: int
    content: str | None = None
    created_at: str
