from aiogram import Router, F
from aiogram.types import Message
from config.risk_config import RISK_PROFILES, DEFAULT_RISK_PROFILE
from bot.keyboards.admin_menu import get_risk_profile_keyboard

router = Router()

current_profile = DEFAULT_RISK_PROFILE


@router.message(F.text == "Admin: Risk Settings")
async def cmd_risk_settings(message: Message):
    profile = RISK_PROFILES[current_profile]
    text = (
        f"*Risk Settings*\n\n"
        f"Active Profile: *{current_profile.upper()}*\n\n"
        f"Max Picks/Day: {profile['max_picks']}\n"
        f"Min Confidence: {profile['min_confidence']*100:.0f}%\n"
        f"Min Value Edge: {profile['min_value_edge']*100:.0f}%\n"
        f"Kelly Fraction: {profile['kelly_fraction']*100:.0f}%\n"
        f"Max Stake: {profile['max_stake_pct']*100:.0f}% of bankroll\n\n"
        f"Select a new profile:"
    )

    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=get_risk_profile_keyboard(),
    )


@router.message(F.text == "Admin: Status")
async def cmd_status(message: Message):
    from data.database import AsyncSessionLocal
    from data.repositories.match_repo import MatchRepository
    from data.repositories.signal_repo import SignalRepository
    from data.repositories.bankroll_repo import BankrollRepository

    async with AsyncSessionLocal() as session:
        match_repo = MatchRepository(session)
        signal_repo = SignalRepository(session)
        bankroll_repo = BankrollRepository(session)

        total_matches = await match_repo.count_all()
        upcoming = await match_repo.get_upcoming()
        signals = await signal_repo.get_latest(limit=1)
        balance = await bankroll_repo.get_current_balance()

    last_signal = signals[0].created_at.strftime("%Y-%m-%d %H:%M") if signals else "None"

    text = (
        f"*System Status*\n\n"
        f"Total Matches in DB: {total_matches}\n"
        f"Upcoming Matches: {len(upcoming)}\n"
        f"Last Signal: {last_signal}\n"
        f"Current Bankroll: ${balance:.2f}\n"
        f"Risk Profile: {current_profile.upper()}\n"
        f"Status: *ONLINE*"
    )

    await message.answer(text, parse_mode="Markdown")
