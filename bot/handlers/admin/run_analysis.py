from aiogram import Router, F
from aiogram.types import Message
from data.database import AsyncSessionLocal
from services.data_fetch.football_data_service import FootballDataService
from services.data_fetch.standings_service import StandingsService
from services.processing.signal_pipeline_service import SignalPipelineService

router = Router()


@router.message(F.text == "Admin: Run Analysis")
async def cmd_run_analysis(message: Message):
    await message.answer("Running signal analysis pipeline...")

    try:
        async with AsyncSessionLocal() as session:
            football_service = FootballDataService()
            standings_service = StandingsService(session, football_service)
            pipeline = SignalPipelineService(session, standings_service)
            signals = await pipeline.execute_full_analysis()

        if signals:
            text = f"*Analysis Complete*\n\n{len(signals)} new signal(s) generated.\n\n"
            for s in signals[:3]:
                match = s.match
                home = match.home_team.name if match and match.home_team else "?"
                away = match.away_team.name if match and match.away_team else "?"
                text += f"  {home} vs {away}: {s.suggested_bet} @ {s.bookmaker_odds}\n"
            await message.answer(text, parse_mode="Markdown")
        else:
            await message.answer("Analysis complete. No value signals found at this time.")
    except Exception as e:
        await message.answer(f"Analysis failed: {str(e)}")
