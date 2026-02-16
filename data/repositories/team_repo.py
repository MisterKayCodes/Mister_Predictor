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

    async def save_team(self, team_data: dict) -> Team:
        """Upsert logic: Update if exists, create if not."""
        team = await self.get_by_external_id(team_data['external_id'])
        if team:
            for key, value in team_data.items():
                setattr(team, key, value)
        else:
            team = Team(**team_data)
            self.session.add(team)
        
        await self.session.flush() # Secure the state without committing the whole transaction
        return team