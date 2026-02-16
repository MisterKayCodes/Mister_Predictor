from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload
from data.models.signal import Signal
from data.models.match import Match
from datetime import datetime, timedelta


class SignalRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _eager_options(self):
        return [
            selectinload(Signal.match).selectinload(Match.home_team),
            selectinload(Signal.match).selectinload(Match.away_team),
        ]

    async def get_latest(self, limit: int = 5) -> list[Signal]:
        result = await self.session.execute(
            select(Signal)
            .options(*self._eager_options())
            .order_by(Signal.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_matchday(self, matchday: int) -> list[Signal]:
        result = await self.session.execute(
            select(Signal)
            .join(Match)
            .where(Match.matchday == matchday)
            .options(*self._eager_options())
            .order_by(Match.utc_date, Signal.rank_in_match)
        )
        return list(result.scalars().all())

    async def get_by_date_range(self, start: datetime, end: datetime) -> list[Signal]:
        result = await self.session.execute(
            select(Signal)
            .join(Match)
            .where(
                Match.utc_date >= start,
                Match.utc_date <= end,
                Match.status.in_(["SCHEDULED", "TIMED"]),
            )
            .options(*self._eager_options())
            .order_by(Match.utc_date, Signal.rank_in_match)
        )
        return list(result.scalars().all())

    async def get_next_matchday_number(self) -> int | None:
        now = datetime.utcnow()
        from sqlalchemy import func as sqlfunc

        result = await self.session.execute(
            select(Match.matchday, Match.utc_date)
            .where(
                Match.status.in_(["SCHEDULED", "TIMED"]),
                Match.utc_date > now,
                Match.matchday != None,
            )
            .order_by(Match.utc_date)
        )
        rows = result.all()
        if not rows:
            return None

        matchday_dates = {}
        for md, dt in rows:
            if md not in matchday_dates:
                matchday_dates[md] = []
            matchday_dates[md].append(dt)

        best_md = None
        best_score = -1
        horizon = now + timedelta(days=10)

        for md, dates in matchday_dates.items():
            dates_in_horizon = [d for d in dates if d <= horizon]
            if not dates_in_horizon:
                continue

            cluster_start = min(dates_in_horizon)
            cluster_end = cluster_start + timedelta(days=4)
            clustered = sum(1 for d in dates if cluster_start <= d <= cluster_end)

            score = clustered * 100 - (cluster_start - now).total_seconds() / 86400
            if score > best_score:
                best_score = score
                best_md = md

        if best_md:
            return best_md

        first_md = rows[0].matchday
        return first_md

    async def get_all_upcoming(self) -> list[Signal]:
        now = datetime.utcnow()
        result = await self.session.execute(
            select(Signal)
            .join(Match)
            .where(
                Match.status.in_(["SCHEDULED", "TIMED"]),
                Match.utc_date > now,
            )
            .options(*self._eager_options())
            .order_by(Match.utc_date, Signal.rank_in_match)
        )
        return list(result.scalars().all())

    async def get_unpublished(self) -> list[Signal]:
        result = await self.session.execute(
            select(Signal)
            .where(Signal.is_published == False)
            .options(*self._eager_options())
            .order_by(Signal.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_match_id(self, match_id: int) -> list[Signal]:
        result = await self.session.execute(
            select(Signal).where(Signal.match_id == match_id).order_by(Signal.rank_in_match)
        )
        return list(result.scalars().all())

    async def add(self, signal: Signal) -> Signal:
        self.session.add(signal)
        await self.session.flush()
        return signal

    async def mark_published(self, signal_id: int):
        result = await self.session.execute(
            select(Signal).where(Signal.id == signal_id)
        )
        signal = result.scalar_one_or_none()
        if signal:
            signal.is_published = True
            await self.session.flush()

    async def delete_for_match(self, match_id: int):
        await self.session.execute(
            delete(Signal).where(
                Signal.match_id == match_id,
                Signal.result_won == None,
            )
        )
        await self.session.flush()

    async def delete_all_pending(self):
        await self.session.execute(
            delete(Signal).where(Signal.result_won == None)
        )
        await self.session.flush()

    async def get_performance_stats(self) -> dict:
        total = await self.session.execute(
            select(func.count(Signal.id)).where(Signal.result_won != None)
        )
        total_count = total.scalar() or 0

        wins = await self.session.execute(
            select(func.count(Signal.id)).where(Signal.result_won == True)
        )
        win_count = wins.scalar() or 0

        return {
            "total_resolved": total_count,
            "wins": win_count,
            "losses": total_count - win_count,
            "win_rate": (win_count / total_count * 100) if total_count > 0 else 0,
        }
