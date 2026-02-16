from aiogram import Router, F
from aiogram.types import Message
from data.database import AsyncSessionLocal
from data.repositories.signal_repo import SignalRepository
from data.repositories.pattern_stat_repo import PatternStatRepository
from bot.keyboards.user_menu import get_performance_keyboard

router = Router()


@router.message(F.text == "Performance")
async def cmd_performance(message: Message):
    async with AsyncSessionLocal() as session:
        signal_repo = SignalRepository(session)
        stats = await signal_repo.get_performance_stats()

    total = stats["total_resolved"]
    if total == 0:
        await message.answer(
            "*Performance Stats*\n\n"
            "No resolved predictions yet.\n"
            "Stats will appear once match results are processed.",
            parse_mode="Markdown",
        )
        return

    text = (
        f"*Performance Stats*\n\n"
        f"Total Predictions: {total}\n"
        f"Wins: {stats['wins']}\n"
        f"Losses: {stats['losses']}\n"
        f"Win Rate: {stats['win_rate']:.1f}%\n"
    )

    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=get_performance_keyboard(),
    )
