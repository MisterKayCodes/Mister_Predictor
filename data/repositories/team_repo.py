from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from data.models.team import Team


class TeamRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_external_id(self, external_id: int) -> Team | None:
        result = await self.session.execute(
            select(Team).where(Team.external_id == external_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Team]:
        result = await self.session.execute(select(Team))
        return list(result.scalars().all())

    async def upsert(self, team_data: dict) -> Team:
        team = await self.get_by_external_id(team_data["external_id"])
        if team:
            for key, value in team_data.items():
                setattr(team, key, value)
        else:
            team = Team(**team_data)
            self.session.add(team)
        await self.session.flush()
        return team
