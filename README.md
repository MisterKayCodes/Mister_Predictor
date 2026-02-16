# Mister Predictor

A Telegram bot that analyzes English Premier League matches to find hidden betting value across 20+ markets.

## What It Does

Mister Predictor watches every EPL match and runs the numbers through a Poisson-based probability model. It compares what the model thinks should happen against what the bookmakers are offering, and flags the gaps — the places where the odds don't match reality.

It doesn't just look at who wins. It digs into niche markets: Both Teams to Score, Over/Under goals at multiple thresholds, Half-Time results, Clean Sheets, Late Goals, Odd/Even totals. That's where the real value hides.

## How It Works

- **Data comes in** from football-data.org (results, scores, standings) and the-odds-api (live bookmaker odds)
- **The brain crunches it** — 25+ features per match, Poisson probability grids, pattern detection across 15+ behavioral signals
- **Value gets surfaced** — the model finds where bookmaker prices are off, ranks the top 3-4 picks per match by edge and consistency
- **You get a clean view** — filtered by Next Matchday, Next 3 Days, This Week, or All Upcoming, with full breakdowns on tap

## Running It

Set your environment variables:

- `BOT_TOKEN` — from Telegram's BotFather
- `FOOTBALL_DATA_API_KEY` — from football-data.org
- `ODDS_API_KEY` — from the-odds-api.com (optional)
- `ADMIN_IDS` — comma-separated Telegram user IDs

Then:

```
python main.py
```

The bot polls Telegram for messages. A daily analysis cycle runs automatically at 05:00 UTC.

## Architecture

Built as a "Living Organism" with strict separation:

- **core/** — Pure math. Probability engines, value detection, pattern recognition, stake sizing. No database, no API calls, no UI.
- **services/** — The nervous system. Fetches data, orchestrates pipelines, schedules jobs.
- **bot/** — The mouth. Telegram interface only. Reply keyboards for navigation, inline keyboards for actions.
- **data/** — The memory. SQLAlchemy models, repositories, Pydantic schemas.

Each layer talks only to its neighbors. The math never touches the database. The bot never does math. Clean lines, no exceptions.

---

*Love From Mister*
