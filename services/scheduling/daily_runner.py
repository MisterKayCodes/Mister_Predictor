import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from data.database import AsyncSessionLocal
from services.data_fetch.football_data_service import FootballDataService
from services.data_fetch.odds_service import OddsService
from services.data_fetch.standings_service import StandingsService
from services.processing.match_preprocessor import MatchPreprocessor
from services.processing.signal_pipeline_service import SignalPipelineService
from services.learning.performance_update_service import PerformanceUpdateService
from data.repositories.match_repo import MatchRepository
from data.repositories.team_repo import TeamRepository
from data.repositories.odds_repo import OddsRepository
from data.repositories.bankroll_repo import BankrollRepository

logger = logging.getLogger(__name__)


class DailyRunner:
    def __init__(self):
        self.football_service = FootballDataService()
        self.odds_service = OddsService()
        self.preprocessor = MatchPreprocessor()

    async def run_daily_cycle(self) -> dict:
        logger.info("Starting Daily Intelligence Cycle...")
        stats = {"teams": 0, "matches": 0, "odds": 0, "standings": 0, "signals": 0}

        async with AsyncSessionLocal() as session:
            try:
                stats["teams"], stats["matches"] = await self._fetch_matches(session)
                stats["standings"] = await self._fetch_standings(session)
                stats["odds"] = await self._fetch_odds(session)
                await self._update_results(session)

                standings_service = StandingsService(session, self.football_service)
                pipeline = SignalPipelineService(session, standings_service)
                signals = await pipeline.execute_full_analysis()
                stats["signals"] = len(signals)

                await session.commit()
            except Exception as e:
                logger.error(f"Daily cycle error: {e}")
                await session.rollback()

        logger.info(f"Daily Cycle Complete: {stats}")
        return stats

    async def _fetch_matches(self, session: AsyncSession) -> tuple[int, int]:
        data = await self.football_service.fetch_epl_matches()
        if not data:
            return 0, 0

        team_repo = TeamRepository(session)
        match_repo = MatchRepository(session)

        matches_raw = data.get("matches", [])
        teams_saved = set()
        match_count = 0

        for api_match in matches_raw:
            for side in ["homeTeam", "awayTeam"]:
                team_data = api_match.get(side, {})
                ext_id = team_data.get("id")
                if ext_id and ext_id not in teams_saved:
                    await team_repo.upsert({
                        "external_id": ext_id,
                        "name": team_data.get("name", "Unknown"),
                        "short_name": team_data.get("shortName", ""),
                        "tla": team_data.get("tla", ""),
                    })
                    teams_saved.add(ext_id)

            normalized = self.preprocessor.normalize_match_data(api_match)

            home_team = await team_repo.get_by_external_id(normalized["home_team_external_id"])
            away_team = await team_repo.get_by_external_id(normalized["away_team_external_id"])

            if home_team and away_team:
                await match_repo.upsert({
                    "external_id": normalized["external_id"],
                    "utc_date": normalized["utc_date"],
                    "status": normalized["status"],
                    "matchday": normalized.get("matchday"),
                    "home_team_id": home_team.id,
                    "away_team_id": away_team.id,
                    "home_score": normalized["home_score"],
                    "away_score": normalized["away_score"],
                    "home_ht_score": normalized.get("home_ht_score"),
                    "away_ht_score": normalized.get("away_ht_score"),
                })
                match_count += 1

        await session.flush()
        logger.info(f"Fetched {len(teams_saved)} teams, {match_count} matches")
        return len(teams_saved), match_count

    async def _fetch_standings(self, session: AsyncSession) -> int:
        standings_service = StandingsService(session, self.football_service)
        return await standings_service.update_standings()

    @staticmethod
    def _normalize_team_name(name: str) -> str:
        n = name.lower().strip()
        for suffix in [" fc", " afc"]:
            if n.endswith(suffix):
                n = n[:-len(suffix)].strip()
        if n.startswith("afc "):
            n = n[4:].strip()
        n = n.replace("&", "and")
        n = n.replace("  ", " ")
        return n

    async def _build_team_lookup(self, session: AsyncSession) -> dict:
        team_repo = TeamRepository(session)
        teams = await team_repo.get_all()
        lookup = {}
        for t in teams:
            lookup[self._normalize_team_name(t.name)] = t.id
            if t.short_name:
                lookup[self._normalize_team_name(t.short_name)] = t.id
        return lookup

    def _find_team_id(self, name: str, lookup: dict) -> int | None:
        normalized = self._normalize_team_name(name)
        if normalized in lookup:
            return lookup[normalized]
        for key, tid in lookup.items():
            if normalized in key or key in normalized:
                return tid
        return None

    async def _fetch_odds(self, session: AsyncSession) -> int:
        raw_odds = await self.odds_service.fetch_latest_odds()
        if not raw_odds:
            return 0

        odds_repo = OddsRepository(session)
        match_repo = MatchRepository(session)
        team_lookup = await self._build_team_lookup(session)
        upcoming = await match_repo.get_upcoming()

        match_lookup = {}
        for m in upcoming:
            key = (m.home_team_id, m.away_team_id)
            match_lookup[key] = m

        count = 0

        for game in raw_odds:
            home_team_name = game.get("home_team", "")
            away_team_name = game.get("away_team", "")

            home_id = self._find_team_id(home_team_name, team_lookup)
            away_id = self._find_team_id(away_team_name, team_lookup)

            if not home_id or not away_id:
                logger.debug(f"Could not match teams: {home_team_name} vs {away_team_name}")
                continue

            match = match_lookup.get((home_id, away_id))
            if not match:
                continue

            bookmakers = game.get("bookmakers", [])
            if not bookmakers:
                continue

            best_home, best_draw, best_away = 0, 0, 0
            totals_by_point = {}
            for bm in bookmakers:
                for market in bm.get("markets", []):
                    mkey = market.get("key")
                    if mkey == "h2h":
                        outcomes = {o["name"]: o["price"] for o in market.get("outcomes", [])}
                        best_home = max(best_home, outcomes.get(home_team_name, 0))
                        best_draw = max(best_draw, outcomes.get("Draw", 0))
                        best_away = max(best_away, outcomes.get(away_team_name, 0))
                    elif mkey == "totals":
                        for o in market.get("outcomes", []):
                            point = o.get("point")
                            name = o.get("name", "")
                            price = o.get("price", 0)
                            if point is not None:
                                key = (name, point)
                                totals_by_point[key] = max(totals_by_point.get(key, 0), price)

            if best_home > 0 and best_draw > 0 and best_away > 0:
                normalized = self.preprocessor.normalize_odds({
                    "home": best_home,
                    "draw": best_draw,
                    "away": best_away,
                })
                normalized["match_id"] = match.id
                normalized["bookmaker"] = "best_available"

                normalized["over_25_odds"] = totals_by_point.get(("Over", 2.5), None)
                normalized["under_25_odds"] = totals_by_point.get(("Under", 2.5), None)
                normalized["over_15_odds"] = totals_by_point.get(("Over", 1.5), None)
                normalized["under_15_odds"] = totals_by_point.get(("Under", 1.5), None)
                normalized["over_35_odds"] = totals_by_point.get(("Over", 3.5), None)
                normalized["under_35_odds"] = totals_by_point.get(("Under", 3.5), None)

                await odds_repo.add_snapshot(normalized)
                count += 1

        await session.flush()
        logger.info(f"Processed {count} odds snapshots")
        return count

    async def _update_results(self, session: AsyncSession):
        perf_service = PerformanceUpdateService(session)

        from sqlalchemy import select
        from data.models.match import Match
        from data.models.signal import Signal

        result = await session.execute(
            select(Match).join(Signal).where(
                Match.status == "FINISHED",
                Signal.result_won == None,
            )
        )
        finished_with_pending = list(result.unique().scalars().all())

        for match in finished_with_pending:
            if match.home_score is None or match.away_score is None:
                continue

            total_goals = match.home_score + match.away_score
            ht_total = None
            if match.home_ht_score is not None and match.away_ht_score is not None:
                ht_total = match.home_ht_score + match.away_ht_score

            outcomes = {
                "HOME_WIN": match.home_score > match.away_score,
                "DRAW": match.home_score == match.away_score,
                "AWAY_WIN": match.away_score > match.home_score,
                "OVER_0.5": total_goals > 0,
                "OVER_1.5": total_goals > 1,
                "OVER_2.5": total_goals > 2,
                "OVER_3.5": total_goals > 3,
                "UNDER_1.5": total_goals < 2,
                "UNDER_2.5": total_goals < 3,
                "UNDER_3.5": total_goals < 4,
                "BTTS_YES": match.home_score > 0 and match.away_score > 0,
                "BTTS_NO": match.home_score == 0 or match.away_score == 0,
                "CLEAN_SHEET_HOME": match.away_score == 0,
                "CLEAN_SHEET_AWAY": match.home_score == 0,
                "ODD_GOALS": total_goals % 2 == 1,
                "EVEN_GOALS": total_goals % 2 == 0,
            }

            if ht_total is not None:
                outcomes["HT_HOME"] = match.home_ht_score > match.away_ht_score
                outcomes["HT_DRAW"] = match.home_ht_score == match.away_ht_score
                outcomes["HT_AWAY"] = match.away_ht_score > match.home_ht_score
                outcomes["HT_OVER_0.5"] = ht_total > 0
                second_half_goals = total_goals - ht_total
                outcomes["LATE_GOAL"] = second_half_goals >= 2

            sig_result = await session.execute(
                select(Signal).where(
                    Signal.match_id == match.id,
                    Signal.result_won == None,
                )
            )
            pending_signals = list(sig_result.scalars().all())

            for sig in pending_signals:
                won = outcomes.get(sig.suggested_bet)
                if won is not None:
                    sig.result_won = won

            await perf_service.process_match_result(match.id, "HOME_WIN" if match.home_score > match.away_score else ("AWAY_WIN" if match.away_score > match.home_score else "DRAW"))
