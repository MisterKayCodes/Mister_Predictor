from aiogram import Router, F
from aiogram.types import Message
from services.scheduling.daily_runner import DailyRunner

router = Router()


@router.message(F.text == "Admin: Update Data")
async def cmd_update_data(message: Message):
    await message.answer("Fetching latest data from APIs... This may take a moment.")

    try:
        runner = DailyRunner()
        stats = await runner.run_daily_cycle()

        await message.answer(
            f"*Data Update Complete*\n\n"
            f"Teams synced: {stats['teams']}\n"
            f"Matches synced: {stats['matches']}\n"
            f"Standings updated: {stats['standings']}\n"
            f"Odds snapshots: {stats['odds']}\n"
            f"New signals: {stats['signals']}",
            parse_mode="Markdown",
        )
    except Exception as e:
        await message.answer(f"Update failed: {str(e)}")
