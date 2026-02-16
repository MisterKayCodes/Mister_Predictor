import logging
from sqlalchemy.ext.asyncio import AsyncSession
from data.repositories.match_repo import MatchRepository
from data.repositories.odds_repo import OddsRepository
from data.repositories.signal_repo import SignalRepository
from data.repositories.bankroll_repo import BankrollRepository
from data.repositories.pattern_stat_repo import PatternStatRepository
from data.models.signal import Signal
from services.processing.feature_builder import FeatureBuilder
from services.data_fetch.standings_service import StandingsService
from core.probability_engine import ProbabilityEngine
from core.value_detector import ValueDetector
from core.pattern_engine import PatternEngine
from core.reliability_tracker import ReliabilityTracker
from core.market_confidence_engine import MarketConfidenceEngine
from core.stake_engine import StakeEngine
from core.signal_engine import SignalEngine
from config.settings import settings

logger = logging.getLogger(__name__)

MAX_SIGNALS_PER_MATCH = 4


class SignalPipelineService:
    def __init__(self, session: AsyncSession, standings_service: StandingsService):
        self.session = session
        self.match_repo = MatchRepository(session)
        self.odds_repo = OddsRepository(session)
        self.signal_repo = SignalRepository(session)
        self.bankroll_repo = BankrollRepository(session)
        self.pattern_stat_repo = PatternStatRepository(session)
        self.standings_service = standings_service

        self.feature_builder = FeatureBuilder()
        self.prob_engine = ProbabilityEngine()
        self.value_detector = ValueDetector(min_edge=settings.MIN_VALUE_EDGE)
        self.pattern_engine = PatternEngine()
        self.reliability_tracker = ReliabilityTracker()
        self.market_conf_engine = MarketConfidenceEngine()
        self.stake_engine = StakeEngine(
            kelly_fraction=settings.DEFAULT_KELLY_FRACTION,
            max_stake_pct=settings.MAX_STAKE_PERCENT,
        )
        self.signal_engine = SignalEngine(min_edge=settings.MIN_VALUE_EDGE)

    async def execute_full_analysis(self) -> list[Signal]:
        generated_signals = []

        matches = await self.match_repo.get_upcoming()
        if not matches:
            logger.info("No upcoming matches to analyze")
            return generated_signals

        standings = await self.standings_service.get_latest_standings()
        bankroll = await self.bankroll_repo.get_current_balance()

        logger.info(f"Analyzing {len(matches)} upcoming matches (Bankroll: {bankroll:.2f})")

        for match in matches:
            try:
                existing = await self.signal_repo.get_by_match_id(match.id)
                if existing:
                    has_old_format = any(s.rank_in_match is None for s in existing)
                    if has_old_format:
                        await self.signal_repo.delete_for_match(match.id)
                    else:
                        continue

                home_history = await self.match_repo.get_home_matches(match.home_team_id)
                away_history = await self.match_repo.get_away_matches(match.away_team_id)

                features = self.feature_builder.build_match_features(
                    match, home_history, away_history, standings
                )

                probs = self.prob_engine.calculate_probs(features)

                patterns = self.pattern_engine.detect_patterns(
                    home_history, away_history, features
                )

                latest_odds = await self.odds_repo.get_latest_for_match(match.id)
                odds_dict = {}
                if latest_odds:
                    odds_dict = {
                        "home_odds": latest_odds.home_odds,
                        "draw_odds": latest_odds.draw_odds,
                        "away_odds": latest_odds.away_odds,
                        "over_25_odds": latest_odds.over_25_odds,
                        "under_25_odds": latest_odds.under_25_odds,
                        "over_15_odds": latest_odds.over_15_odds,
                        "under_15_odds": latest_odds.under_15_odds,
                        "over_35_odds": latest_odds.over_35_odds,
                        "under_35_odds": latest_odds.under_35_odds,
                    }

                value_markets = self.value_detector.evaluate_all_markets(probs, odds_dict, features)

                if not value_markets:
                    continue

                pattern_stats = []
                for p in patterns:
                    stat = await self.pattern_stat_repo.get_by_name(p["name"])
                    if stat:
                        pattern_stats.append({
                            "win_rate": stat.reliability_score,
                            "sample_size": stat.occurrences,
                        })

                odds_snapshots = await self.odds_repo.get_all_for_match(match.id)
                odds_history_dicts = [
                    {"home_odds": o.home_odds, "away_odds": o.away_odds}
                    for o in odds_snapshots
                ]

                diverse_markets = self._diversify_markets(value_markets, MAX_SIGNALS_PER_MATCH)

                match_signals = []
                for vm in diverse_markets:
                    relevant_patterns = self._get_relevant_patterns(patterns, vm["bet_type"])

                    base_confidence = vm["predicted_prob"]
                    adjusted_confidence = self.reliability_tracker.adjust_confidence(
                        base_confidence, pattern_stats
                    )

                    consistency = vm.get("consistency", self._calc_consistency(vm, features))

                    pattern_boost = 0.05 * len(relevant_patterns)
                    adjusted_confidence = min(1.0, adjusted_confidence + pattern_boost)

                    market_conf = self.market_conf_engine.get_score(
                        vm["bet_type"], odds_history_dicts
                    )

                    stake = self.stake_engine.calculate_kelly_stake(
                        bankroll, vm["odds"], adjusted_confidence
                    )

                    decision = self.signal_engine.generate_final_decision(
                        prob_report=probs,
                        value_edge=vm["edge"],
                        confidence_score=adjusted_confidence,
                        stake_amount=stake,
                        bet_type=vm["bet_type"],
                        patterns=relevant_patterns,
                        market_confidence=market_conf,
                    )

                    if decision["decision"] == "BET":
                        pattern_names = ",".join(p["name"] for p in relevant_patterns) if relevant_patterns else None
                        match_signals.append({
                            "vm": vm,
                            "decision": decision,
                            "pattern_names": pattern_names,
                            "consistency": consistency,
                        })

                for rank, sig_data in enumerate(match_signals, 1):
                    vm = sig_data["vm"]
                    decision = sig_data["decision"]

                    signal = Signal(
                        match_id=match.id,
                        market_key=vm.get("market_key", "1x2"),
                        suggested_bet=decision["bet_type"],
                        predicted_prob=vm["predicted_prob"],
                        implied_prob=vm["implied_prob"],
                        value_edge=decision["edge"],
                        bookmaker_odds=vm["odds"],
                        confidence_score=decision["confidence"],
                        market_confidence=decision["market_confidence"],
                        recommended_stake=decision["stake"],
                        consistency_pct=sig_data["consistency"],
                        rank_in_match=rank,
                        patterns_detected=sig_data["pattern_names"],
                        explanation=decision["explanation"],
                    )
                    await self.signal_repo.add(signal)
                    generated_signals.append(signal)

                if match_signals:
                    match.predicted_home_win_prob = probs["home"]
                    match.predicted_draw_prob = probs["draw"]
                    match.predicted_away_win_prob = probs["away"]

                    home_name = match.home_team.name if match.home_team else "?"
                    away_name = match.away_team.name if match.away_team else "?"
                    bet_summary = ", ".join(
                        f"{s['decision']['bet_type']}@{s['vm']['odds']}"
                        for s in match_signals
                    )
                    logger.info(
                        f"SIGNALS ({len(match_signals)}): {home_name} vs {away_name} | {bet_summary}"
                    )

            except Exception as e:
                logger.error(f"Error analyzing match {match.id}: {e}")
                continue

        await self.session.commit()
        logger.info(f"Pipeline complete. {len(generated_signals)} signals generated.")
        return generated_signals

    def _get_relevant_patterns(self, patterns: list, bet_type: str) -> list:
        relevant = []
        for p in patterns:
            supported_markets = p.get("markets", [])
            if not supported_markets:
                relevant.append(p)
            elif bet_type in supported_markets:
                relevant.append(p)
        return relevant

    def _diversify_markets(self, value_markets: list, max_picks: int) -> list:
        selected = []
        seen_categories = set()

        for vm in value_markets:
            category = vm.get("market_key", "1x2")
            if category not in seen_categories:
                selected.append(vm)
                seen_categories.add(category)
                if len(selected) >= max_picks:
                    break

        if len(selected) < max_picks:
            for vm in value_markets:
                if vm not in selected:
                    selected.append(vm)
                    if len(selected) >= max_picks:
                        break

        return selected

    def _calc_consistency(self, value_market: dict, features: dict) -> float:
        if not features:
            return 0.5
        bt = value_market["bet_type"]
        mapping = {
            "OVER_2.5": "over_25_home_rate",
            "OVER_1.5": "over_15_home_rate",
            "OVER_3.5": "over_35_home_rate",
            "HOME_WIN": "home_form_avg",
            "AWAY_WIN": "away_form_avg",
        }
        key = mapping.get(bt)
        if key and key in features:
            return features[key]
        if bt.startswith("UNDER_"):
            over_bt = bt.replace("UNDER_", "OVER_")
            over_key = mapping.get(over_bt)
            if over_key and over_key in features:
                return 1.0 - features[over_key]
        return value_market.get("predicted_prob", 0.5)
