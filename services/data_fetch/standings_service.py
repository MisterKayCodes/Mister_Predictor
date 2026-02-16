import logging
from services.data_fetch.football_data_service import FootballDataService
from data.repositories.team_repo import TeamRepository
from data.models.standing_snapshot import StandingSnapshot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class StandingsService:
    def __init__(self, session: AsyncSession, football_service: FootballDataService):
        self.session = session
        self.football_service = football_service
        self.team_repo = TeamRepository(session)

    async def update_standings(self) -> int:
        data = await self.football_service.fetch_epl_standings()
        if not data:
            logger.warning("No standings data received")
            return 0

        standings_list = data.get("standings", [])
        if not standings_list:
            return 0

        total_table = None
        for table in standings_list:
            if table.get("type") == "TOTAL":
                total_table = table.get("table", [])
                break

        if not total_table:
            total_table = standings_list[0].get("table", [])

        count = 0
        batch_time = datetime.utcnow()
        for entry in total_table:
            team_api = entry.get("team", {})
            team = await self.team_repo.get_by_external_id(team_api.get("id"))
            if not team:
                continue

            snapshot = StandingSnapshot(
                team_id=team.id,
                position=entry.get("position"),
                played=entry.get("playedGames", 0),
                wins=entry.get("won", 0),
                draws=entry.get("draw", 0),
                losses=entry.get("lost", 0),
                points=entry.get("points", 0),
                goals_for=entry.get("goalsFor", 0),
                goals_against=entry.get("goalsAgainst", 0),
                goal_diff=entry.get("goalDifference", 0),
                snapshot_date=batch_time,
            )
            self.session.add(snapshot)
            count += 1

        await self.session.flush()
        logger.info(f"Updated standings for {count} teams")
        return count

    async def get_latest_standings(self) -> list[StandingSnapshot]:
        result = await self.session.execute(
            select(StandingSnapshot)
            .order_by(StandingSnapshot.snapshot_date.desc())
            .limit(20)
        )
        return list(result.scalars().all())
