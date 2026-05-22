"""通用请求/响应模型，分页模型"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """统一 API 响应格式"""
    code: int = 0
    message: str = "ok"
    data: T | None = None

    @classmethod
    def success(cls, data: T = None, message: str = "ok") -> "APIResponse[T]":
        return cls(code=0, message=message, data=data)

    @classmethod
    def error(cls, code: int, message: str, data: Any = None) -> "APIResponse":
        return cls(code=code, message=message, data=data)


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedData(BaseModel, Generic[T]):
    """分页响应数据"""
    items: list[T] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0


class PaginatedResponse(APIResponse[PaginatedData[T]], Generic[T]):
    """分页 API 响应"""
    pass


def paginate(items: list[T], total: int, page: int, page_size: int) -> PaginatedData[T]:
    """构建分页响应数据"""
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedData(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
