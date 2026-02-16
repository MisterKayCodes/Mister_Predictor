import ast
import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_imports(filepath: str) -> list[str]:
    with open(filepath, "r") as f:
        tree = ast.parse(f.read())
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def test_core_is_pure_brain():
    core_dir = "core"
    violations = []
    for filename in os.listdir(core_dir):
        if not filename.endswith(".py") or filename == "__init__.py":
            continue
        filepath = os.path.join(core_dir, filename)
        imports = get_imports(filepath)
        for imp in imports:
            if any(
                imp.startswith(prefix)
                for prefix in ["data.", "bot.", "services.", "sqlalchemy", "aiogram", "httpx"]
            ):
                violations.append(f"{filename} imports {imp}")
    assert not violations, f"Core (Brain) has forbidden imports: {violations}"
    print("PASS: Core layer is pure math - no DB/API/UI imports")


def test_bot_has_no_core_math():
    bot_dir = "bot"
    violations = []
    for root, dirs, files in os.walk(bot_dir):
        for filename in files:
            if not filename.endswith(".py") or filename == "__init__.py":
                continue
            filepath = os.path.join(root, filename)
            imports = get_imports(filepath)
            for imp in imports:
                if imp.startswith("core."):
                    violations.append(f"{filepath} imports {imp}")
    assert not violations, f"Bot (Mouth) has core imports: {violations}"
    print("PASS: Bot layer has no core math imports")


def test_bot_has_no_direct_db_queries():
    bot_dir = "bot"
    violations = []
    for root, dirs, files in os.walk(bot_dir):
        for filename in files:
            if not filename.endswith(".py") or filename == "__init__.py":
                continue
            filepath = os.path.join(root, filename)
            imports = get_imports(filepath)
            for imp in imports:
                if imp.startswith("data.models."):
                    violations.append(f"{filepath} imports model directly: {imp}")
    assert not violations, f"Bot has direct model imports: {violations}"
    print("PASS: Bot layer uses repositories, not direct model access")


def test_core_engines_instantiate():
    from core.probability_engine import ProbabilityEngine
    from core.value_detector import ValueDetector
    from core.pattern_engine import PatternEngine
    from core.reliability_tracker import ReliabilityTracker
    from core.market_confidence_engine import MarketConfidenceEngine
    from core.stake_engine import StakeEngine
    from core.signal_engine import SignalEngine

    prob = ProbabilityEngine()
    val = ValueDetector()
    pat = PatternEngine()
    rel = ReliabilityTracker()
    mkt = MarketConfidenceEngine()
    stk = StakeEngine()
    sig = SignalEngine()
    print("PASS: All core engines instantiate correctly")


def test_probability_engine():
    from core.probability_engine import ProbabilityEngine

    engine = ProbabilityEngine()
    features = {
        "home_form_avg": 0.6,
        "away_form_avg": 0.3,
        "position_gap": 5,
        "goals_avg": 2.5,
        "defensive_strength": 0.7,
    }
    result = engine.calculate_probs(features)
    assert "home" in result
    assert "draw" in result
    assert "away" in result
    total = result["home"] + result["draw"] + result["away"]
    assert abs(total - 1.0) < 0.01, f"Probabilities don't sum to 1: {total}"
    print(f"PASS: Probability engine output: {result}")


def test_value_detector():
    from core.value_detector import ValueDetector

    detector = ValueDetector(min_edge=0.05)
    edge = detector.find_edge(pred_prob=0.55, market_prob=0.45)
    assert abs(edge - 0.10) < 0.001, f"Edge calculation wrong: {edge}"

    markets = detector.evaluate_all_markets(
        probs={"home": 0.55, "draw": 0.25, "away": 0.20},
        odds={"home_odds": 2.0, "draw_odds": 3.5, "away_odds": 5.0},
    )
    assert len(markets) > 0, "Should find at least one value market"
    print(f"PASS: Value detector found {len(markets)} value market(s)")


def test_stake_engine():
    from core.stake_engine import StakeEngine

    engine = StakeEngine(kelly_fraction=0.1, max_stake_pct=0.05)
    stake = engine.calculate_kelly_stake(bankroll=1000, odds=2.0, prob=0.55)
    assert stake > 0, "Should recommend a positive stake"
    assert stake <= 50, f"Stake exceeds 5% cap: {stake}"
    print(f"PASS: Stake engine recommends ${stake}")


def test_signal_engine():
    from core.signal_engine import SignalEngine

    engine = SignalEngine(min_edge=0.05, min_confidence=0.5)
    decision = engine.generate_final_decision(
        prob_report={"home": 0.55, "draw": 0.25, "away": 0.20},
        value_edge=0.10,
        confidence_score=0.65,
        stake_amount=25.0,
        bet_type="HOME_WIN",
        patterns=[{"name": "HOME_FORTRESS"}],
        market_confidence=0.7,
    )
    assert decision["decision"] == "BET"
    assert decision["stake"] == 25.0
    print(f"PASS: Signal engine decision: {decision['decision']}")


def test_pattern_engine():
    from core.pattern_engine import PatternEngine

    engine = PatternEngine()
    patterns = engine.detect_patterns([], [], {"position_gap": 10})
    assert any(p["name"] == "CLASS_GAP" for p in patterns)
    print(f"PASS: Pattern engine detected {len(patterns)} pattern(s)")


def test_database_init():
    async def _test():
        from data.database import init_db, engine
        await init_db()
        print("PASS: Database tables created successfully")

    asyncio.run(_test())


def test_idempotent_upsert():
    async def _test():
        from data.database import init_db, AsyncSessionLocal
        from data.repositories.team_repo import TeamRepository

        await init_db()
        async with AsyncSessionLocal() as session:
            repo = TeamRepository(session)
            team1 = await repo.upsert({"external_id": 99999, "name": "Test FC", "tla": "TST"})
            await session.commit()

            team2 = await repo.upsert({"external_id": 99999, "name": "Test FC Updated", "tla": "TST"})
            await session.commit()

            assert team1.id == team2.id, "Upsert should return same record"
            assert team2.name == "Test FC Updated"
            print("PASS: Upsert is idempotent")

    asyncio.run(_test())


if __name__ == "__main__":
    tests = [
        test_core_is_pure_brain,
        test_bot_has_no_core_math,
        test_bot_has_no_direct_db_queries,
        test_core_engines_instantiate,
        test_probability_engine,
        test_value_detector,
        test_stake_engine,
        test_signal_engine,
        test_pattern_engine,
        test_database_init,
        test_idempotent_upsert,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__} - {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print(f"{'='*50}")
