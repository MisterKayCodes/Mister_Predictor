from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from data.models.pattern_stat import PatternStat


class PatternStatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_name(self, name: str) -> PatternStat | None:
        result = await self.session.execute(
            select(PatternStat).where(PatternStat.pattern_name == name)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[PatternStat]:
        result = await self.session.execute(select(PatternStat))
        return list(result.scalars().all())

    async def update_reliability(self, name: str, is_win: bool) -> PatternStat:
        stat = await self.get_by_name(name)
        if not stat:
            stat = PatternStat(
                pattern_name=name,
                occurrences=1,
                wins=1 if is_win else 0,
                losses=0 if is_win else 1,
            )
            self.session.add(stat)
        else:
            stat.occurrences += 1
            if is_win:
                stat.wins += 1
            else:
                stat.losses += 1
            stat.reliability_score = stat.wins / stat.occurrences if stat.occurrences > 0 else 0

        await self.session.flush()
        return stat
