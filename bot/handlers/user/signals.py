from aiogram import Router, F
from aiogram.types import Message
from data.database import AsyncSessionLocal
from data.repositories.signal_repo import SignalRepository
from bot.keyboards.user_menu import get_signal_filter_keyboard, get_signal_details_keyboard
from bot.signal_view_helpers import build_signals_response, group_and_format

router = Router()


@router.message(F.text == "Signals")
async def cmd_signals(message: Message):
    async with AsyncSessionLocal() as session:
        signal_repo = SignalRepository(session)
        header, signals = await build_signals_response(signal_repo, "matchday")

    results = group_and_format(header, signals)
    keyboard = get_signal_filter_keyboard(active="matchday")

    if results:
        await message.answer(results[0]["text"], parse_mode="HTML", reply_markup=keyboard)
        for item in results[1:]:
            detail_kb = get_signal_details_keyboard(item["first_signal_id"]) if item["first_signal_id"] else None
            await message.answer(item["text"], parse_mode="HTML", reply_markup=detail_kb)
