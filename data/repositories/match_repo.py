from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from data.models.match import Match
from datetime import datetime


class MatchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_upcoming(self) -> list[Match]:
        result = await self.session.execute(
            select(Match)
            .where(
                Match.status.in_(["SCHEDULED", "TIMED"]),
                Match.utc_date > datetime.utcnow(),
            )
            .options(selectinload(Match.home_team), selectinload(Match.away_team))
            .order_by(Match.utc_date)
        )
        return list(result.scalars().all())

    async def get_finished_without_signal(self) -> list[Match]:
        from data.models.signal import Signal
        from sqlalchemy import not_, exists
        result = await self.session.execute(
            select(Match)
            .where(
                Match.status == "FINISHED",
                not_(exists().where(Signal.match_id == Match.id))
            )
            .options(selectinload(Match.home_team), selectinload(Match.away_team))
        )
        return list(result.scalars().all())

    async def get_recent_by_team(self, team_id: int, limit: int = 10) -> list[Match]:
        result = await self.session.execute(
            select(Match)
            .where(
                Match.status == "FINISHED",
                (Match.home_team_id == team_id) | (Match.away_team_id == team_id),
            )
            .order_by(Match.utc_date.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_home_matches(self, team_id: int, limit: int = 10) -> list[Match]:
        result = await self.session.execute(
            select(Match)
            .where(Match.status == "FINISHED", Match.home_team_id == team_id)
            .order_by(Match.utc_date.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_away_matches(self, team_id: int, limit: int = 10) -> list[Match]:
        result = await self.session.execute(
            select(Match)
            .where(Match.status == "FINISHED", Match.away_team_id == team_id)
            .order_by(Match.utc_date.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def upsert(self, match_data: dict) -> Match:
        result = await self.session.execute(
            select(Match).where(Match.external_id == match_data["external_id"])
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

    async def get_recent_finished(self, limit: int = 15) -> list[Match]:
        result = await self.session.execute(
            select(Match)
            .where(Match.status == "FINISHED")
            .options(selectinload(Match.home_team), selectinload(Match.away_team))
            .order_by(Match.utc_date.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_all(self) -> int:
        result = await self.session.execute(select(Match))
        return len(list(result.scalars().all()))
