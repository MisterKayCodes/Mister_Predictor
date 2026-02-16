from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from data.models.odds import Odds


class OddsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_latest_for_match(self, match_id: int) -> Odds | None:
        result = await self.session.execute(
            select(Odds)
            .where(Odds.match_id == match_id)
            .order_by(Odds.recorded_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_all_for_match(self, match_id: int) -> list[Odds]:
        result = await self.session.execute(
            select(Odds)
            .where(Odds.match_id == match_id)
            .order_by(Odds.recorded_at)
        )
        return list(result.scalars().all())

    async def add_snapshot(self, odds_data: dict) -> Odds:
        new_odds = Odds(**odds_data)
        self.session.add(new_odds)
        await self.session.flush()
        return new_odds
