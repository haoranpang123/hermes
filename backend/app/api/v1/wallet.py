"""钱包 API"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps.auth import require_parent
from app.api.deps.pagination import pagination
from app.services.wallet_service import WalletService
from app.models.user import User
from app.schemas.wallet import RechargeRequest, RechargeResponse, WalletOverview
from app.schemas.common import APIResponse, PaginationParams, paginate

router = APIRouter(prefix="/wallet", tags=["钱包"])


@router.get("", response_model=APIResponse[WalletOverview])
async def get_wallet(
    user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_db),
):
    """钱包余额与概览"""
    svc = WalletService(db)
    result = await svc.get_wallet(user)
    return APIResponse.success(data=result)


@router.get("/transactions", response_model=APIResponse)
async def get_transactions(
    user: User = Depends(require_parent),
    pagination: PaginationParams = Depends(pagination),
    db: AsyncSession = Depends(get_db),
):
    """交易流水列表"""
    svc = WalletService(db)
    items, total = await svc.get_transactions(user, pagination.page, pagination.page_size)
    return APIResponse.success(data=paginate(items, total, pagination.page, pagination.page_size))


@router.post("/recharge", response_model=APIResponse[RechargeResponse])
async def recharge(
    req: RechargeRequest,
    user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_db),
):
    """创建充值订单"""
    svc = WalletService(db)
    result = await svc.recharge(user, req)
    return APIResponse.success(data=result)
