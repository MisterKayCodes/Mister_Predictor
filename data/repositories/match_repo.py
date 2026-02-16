from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from data.models.match import Match, MatchStatus
from datetime import datetime

class MatchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_upcoming_matches(self):
        """Used by the Brain to find what to analyze next."""
        result = await self.session.execute(
            select(Match).where(
                Match.status == MatchStatus.SCHEDULED,
                Match.utc_date > datetime.utcnow()
            )
        )
        return result.scalars().all()

    async def upsert_match(self, match_data: dict) -> Match:
        result = await self.session.execute(
            select(Match).where(Match.external_id == match_data['external_id'])
        )
        match = result.scalar_one_or_none()
        
        if match:
            for key, value in match_data.items():
                setattr(match, key, value)
        else:
            match = Match(**match_data)
            self.session.add(match)
            
        await self.session.flush()
        return match