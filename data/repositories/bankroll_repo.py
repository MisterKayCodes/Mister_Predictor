from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from data.models.bankroll import BankrollHistory
from config.settings import settings


class BankrollRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_current_balance(self) -> float:
        result = await self.session.execute(
            select(BankrollHistory)
            .order_by(BankrollHistory.timestamp.desc())
            .limit(1)
        )
        entry = result.scalar_one_or_none()
        return entry.balance if entry else settings.DEFAULT_BANKROLL

    async def get_history(self, limit: int = 20) -> list[BankrollHistory]:
        result = await self.session.execute(
            select(BankrollHistory)
            .order_by(BankrollHistory.timestamp.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_balance(self, new_balance: float, pnl: float = 0, stake: float = 0, match_id: int = None):
        entry = BankrollHistory(
            balance=new_balance,
            pnl=pnl,
            stake=stake,
            match_id=match_id,
        )
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def initialize_if_empty(self):
        result = await self.session.execute(
            select(BankrollHistory).limit(1)
        )
        if result.scalar_one_or_none() is None:
            entry = BankrollHistory(balance=settings.DEFAULT_BANKROLL, pnl=0)
            self.session.add(entry)
            await self.session.flush()
