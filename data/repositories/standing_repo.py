from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from data.models.standing_snapshot import StandingSnapshot


class StandingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_latest(self) -> list[StandingSnapshot]:
        result = await self.session.execute(
            select(StandingSnapshot)
            .options(selectinload(StandingSnapshot.team))
            .order_by(StandingSnapshot.position)
        )
        snapshots = list(result.scalars().all())
        if not snapshots:
            return []
        latest_date = max(s.snapshot_date for s in snapshots)
        return [s for s in snapshots if s.snapshot_date == latest_date]
