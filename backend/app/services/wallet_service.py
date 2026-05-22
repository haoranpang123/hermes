"""钱包服务 — 余额 / 充值 / 交易流水 / 虚拟币扣减"""

from datetime import datetime

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.exceptions import BusinessError, NotFoundError
from app.models.user import User
from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction
from app.schemas.wallet import (
    WalletOverview,
    RechargeRequest,
    RechargeResponse,
    TransactionItem,
)

settings = get_settings()


class WalletService:
    """钱包服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_wallet(self, user: User) -> Wallet:
        result = await self.db.execute(select(Wallet).where(Wallet.user_id == user.user_id))
        wallet = result.scalar_one_or_none()
        if not wallet:
            wallet = Wallet(user_id=user.user_id, balance=0)
            self.db.add(wallet)
            await self.db.flush()
        return wallet

    async def get_wallet(self, user: User) -> WalletOverview:
        wallet = await self.get_or_create_wallet(user)
        return WalletOverview(
            balance=wallet.balance,
            total_recharged=wallet.total_recharged,
            total_spent=wallet.total_spent,
        )

    async def recharge(self, user: User, req: RechargeRequest) -> RechargeResponse:
        """充值 (创建充值订单，返回微信支付参数)"""
        # MVP: 直接增加余额 (生产环境需微信支付回调)
        wallet = await self.get_or_create_wallet(user)
        coins = req.amount  # 1元 = 1币

        wallet.balance += coins
        wallet.total_recharged += coins

        # 记录流水
        txn = WalletTransaction(
            user_id=user.user_id,
            type="recharge",
            amount=coins,
            balance_after=wallet.balance,
            description=f"充值 {coins} 币",
            ref_type="recharge",
            created_at=datetime.now(),
        )
        self.db.add(txn)
        await self.db.flush()

        return RechargeResponse(
            recharge_id=txn.transaction_id,
            amount=req.amount,
            coins=coins,
            wechat_pay_params={"mock": True, "message": "MVP跳过微信支付"},
        )

    async def get_transactions(self, user: User, page: int, page_size: int) -> tuple[list[TransactionItem], int]:
        """交易流水列表"""
        count_result = await self.db.execute(
            select(func.count(WalletTransaction.transaction_id)).where(
                WalletTransaction.user_id == user.user_id
            )
        )
        total = count_result.scalar() or 0

        result = await self.db.execute(
            select(WalletTransaction)
            .where(WalletTransaction.user_id == user.user_id)
            .order_by(desc(WalletTransaction.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        txns = result.scalars().all()

        items = [
            TransactionItem(
                transaction_id=t.transaction_id,
                type=t.type,
                amount=t.amount,
                balance_after=t.balance_after,
                description=t.description,
                created_at=str(t.created_at),
            )
            for t in txns
        ]
        return items, total

    async def consume_coins(self, user: User, amount: int, description: str, ref_id: int | None = None, ref_type: str | None = None) -> dict:
        """
        虚拟币扣减 (SELECT ... FOR UPDATE 悲观锁)
        用于: 查看教师联系方式
        """
        # 行锁查询
        result = await self.db.execute(
            select(Wallet).where(Wallet.user_id == user.user_id).with_for_update()
        )
        wallet = result.scalar_one_or_none()
        if not wallet:
            wallet = Wallet(user_id=user.user_id, balance=0)
            self.db.add(wallet)
            await self.db.flush()
            # Re-fetch with lock
            result = await self.db.execute(
                select(Wallet).where(Wallet.user_id == user.user_id).with_for_update()
            )
            wallet = result.scalar_one()

        if wallet.balance < amount:
            raise BusinessError(
                f"虚拟币余额不足，当前余额{wallet.balance}币，需要{amount}币",
                data={
                    "current_balance": wallet.balance,
                    "required": amount,
                    "shortage": amount - wallet.balance,
                },
            )

        wallet.balance -= amount
        wallet.total_spent += amount

        txn = WalletTransaction(
            user_id=user.user_id,
            type="consume",
            amount=-amount,
            balance_after=wallet.balance,
            description=description,
            ref_id=ref_id,
            ref_type=ref_type,
            created_at=datetime.now(),
        )
        self.db.add(txn)
        await self.db.flush()

        return {
            "consumed_coins": amount,
            "balance_after": wallet.balance,
        }
