from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from data.models.odds import Odds

class OddsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_latest_for_match(self, match_id: int) -> Odds | None:
        """Gets the most recent odds snapshot for a specific match."""
        result = await self.session.execute(
            select(Odds)
            .where(Odds.match_id == match_id)
            .order_by(Odds.recorded_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def add_odds_snapshot(self, odds_data: dict):
        """Records a new point in the odds history."""
        new_odds = Odds(**odds_data)
        self.session.add(new_odds)
        await self.session.flush()
        return new_odds