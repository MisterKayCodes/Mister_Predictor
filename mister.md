# Mister Predictor - Football Intelligence & Value Detection System

## Overview
A Telegram-based automated football intelligence system (EPL-focused) that analyzes team behavior, detects bookmaker mispricing, ranks value opportunities, optimizes bet combinations, and manages bankroll growth using structured mathematical decision logic.

## Architecture - "Living Organism" Design

### core/ (The Brain)
Pure mathematical engines. No DB, API, or UI imports allowed.
- `probability_engine.py` - Calculates match outcome probabilities
- `value_detector.py` - Finds mispriced outcomes (model vs market)
- `pattern_engine.py` - Detects repeatable team behaviors
- `reliability_tracker.py` - Adjusts confidence based on pattern history
- `market_confidence_engine.py` - Evaluates odds movement significance
- `stake_engine.py` - Kelly criterion stake sizing with safety caps
- `signal_engine.py` - Final BET/PASS decision maker

### services/ (The Nervous System)
Handles APIs, orchestration, and data flow. No direct math.
- `data_fetch/` - Football data API, odds API, standings service
- `processing/` - Feature builder, match preprocessor, signal pipeline
- `learning/` - Pattern learning, performance updates
- `scheduling/` - Daily automated runner

### bot/ (The Mouth)
Telegram UI only. No math or direct DB queries.
- `handlers/user/` - start, signals, bankroll, performance, browse_data
- `handlers/admin/` - update_data, run_analysis, risk_control
- `keyboards/` - Reply keyboards (main menu) + Inline keyboards (actions)
- `middlewares/` - Auth (admin check) + logging
- `callbacks.py` - Inline button callback handlers
- `bot_factory.py` - Bot and dispatcher creation

### data/ (The Memory)
All persistence via Repository pattern.
- `models/` - SQLAlchemy ORM models (team, match, odds, signal, bankroll, pattern_stat, standing_snapshot)
- `repositories/` - Repository classes for each model
- `schemas/` - Pydantic validation schemas
- `database.py` - Engine and session factory (SQLite)

### config/
- `settings.py` - Central settings via pydantic-settings
- `bot_config.py` - Bot command definitions
- `risk_config.py` - Risk profile configurations (conservative/balanced/aggressive)

### utils/
- `odds.py` - Odds conversion helpers
- `formatters.py` - Signal message formatting
- `logging.py` - Logging setup
- `time.py` - UTC/timezone helpers

## Database
SQLite via aiosqlite + SQLAlchemy async. File: `mister_predictor.db`

## Environment Variables Required
- `BOT_TOKEN` - Telegram bot token from @BotFather
- `FOOTBALL_DATA_API_KEY` - API key from football-data.org
- `ODDS_API_KEY` - API key from the-odds-api.com (optional)
- `ADMIN_IDS` - Comma-separated Telegram user IDs for admin access

## Running
```bash
python main.py
```
Bot runs in polling mode with BOT_TOKEN, or headless mode without it.
Daily analysis cycle runs at 05:00 UTC (configurable).

## Multi-Market Analysis System
The system analyzes 10+ betting markets per match using a Poisson-based probability model:

### Markets with Bookmaker Odds (from the-odds-api)
- 1X2 (Home/Draw/Away)
- Over/Under 1.5, 2.5, 3.5 goals

### Model-Only Markets (no bookmaker odds available, fair odds computed internally)
- BTTS Yes/No
- Clean Sheet Home/Away
- Odd/Even Total Goals
- Half-Time 1X2
- Half-Time Over 0.5 Goals
- Late Goal (2+ second-half goals)

### Pipeline Flow
1. FeatureBuilder computes ~25 features per match (form, xG, HT stats, BTTS rate, clean sheet rate, late goals, etc.)
2. ProbabilityEngine uses Poisson grid model to compute probabilities for all markets
3. ValueDetector evaluates all markets against bookmaker odds (where available) or model-implied fair odds
4. PatternEngine detects 15+ behavioral patterns with market-specific relevance
5. Top 3-4 value picks ranked per match by edge and consistency
6. Bot displays grouped signals per match with confidence and consistency ratings

### Data Sources
- football-data.org: Match results + half-time scores (used for all stat computation)
- the-odds-api: h2h + totals markets (h2h, totals, spreads supported; btts/niche NOT supported)

## Recent Changes
- 2026-02-16: Initial complete implementation of all layers
- Fixed broken models (odds.py had wrong class, bankroll.py missing imports)
- Fixed duplicate repository (bankroll_repo was copy of odds_repo)
- Implemented full bot layer with aiogram v3
- Added mixed navigation: Reply Keyboards (persistent menu) + Inline Keyboards (dynamic actions)
- Created signal pipeline orchestration
- Added architecture validation tests (11/11 passing)
- Added "Browse Data" button with inline views: Upcoming Matches, Recent Results, League Standings, Live Odds
- Added standing_repo.py and match_repo.get_recent_finished() for data browsing
- 2026-02-16: Multi-market expansion
  - Match model: added home_ht_score, away_ht_score columns
  - Signal model: added market_key, consistency_pct, rank_in_match; changed to multi-signal per match
  - Odds model: added over/under 1.5/2.5/3.5 odds columns
  - ProbabilityEngine: Poisson grid model for all markets (was linear formula for 1X2 only)
  - ValueDetector: evaluates all markets, model-only markets use typical margin for edge calc
  - PatternEngine: 15+ patterns with market relevance tags
  - FeatureBuilder: ~25 features including HT stats, BTTS rate, clean sheet rate, late goals
  - SignalPipeline: generates up to 4 signals per match across all markets
  - Bot signals display: grouped per match with ranked picks, market labels, consistency scores
  - _update_results: resolves all market types (BTTS, O/U, HT, clean sheet, odd/even, late goal)
  - OddsService: fetches h2h + totals markets from the-odds-api
- 2026-02-16: Signal filtering & smart matchday selection
  - Added inline filter buttons: Next Matchday (default), Next 3 Days, This Week, All Upcoming
  - Smart matchday selection algorithm scores matchdays by cluster density (clustered_matches * 100 - days_until) to prefer compact rounds over scattered rescheduled fixtures
  - Moved shared signal view logic to bot/signal_view_helpers.py to eliminate circular dependencies
  - Per-match detail buttons with full analysis breakdown
  - Fixed ValueDetector bias: realistic typical odds benchmarks for model-only markets, market diversification
  - Signal distribution now diverse: LATE_GOAL, HT_HOME, BTTS_YES/NO, HOME/AWAY_WIN across 120 matches
