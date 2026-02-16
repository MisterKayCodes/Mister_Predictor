from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from data.models.signal import Signal

class SignalRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_latest_signals(self, limit: int = 5):
        """Fetches the newest intelligence for the /signals command."""
        result = await self.session.execute(
            select(Signal).order_by(Signal.created_at.desc()).limit(limit)
        )
        return result.scalars().all()

    async def add_signal(self, signal: Signal):
        self.session.add(signal)
        await self.session.flush()