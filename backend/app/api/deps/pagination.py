"""分页参数依赖"""

from fastapi import Query

from app.schemas.common import PaginationParams


async def pagination(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)
