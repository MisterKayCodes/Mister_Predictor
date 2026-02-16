from aiogram import Router, F
from aiogram.types import Message
from data.database import AsyncSessionLocal
from data.repositories.bankroll_repo import BankrollRepository
from bot.keyboards.user_menu import get_bankroll_keyboard

router = Router()


@router.message(F.text == "Bankroll")
async def cmd_bankroll(message: Message):
    async with AsyncSessionLocal() as session:
        bankroll_repo = BankrollRepository(session)
        balance = await bankroll_repo.get_current_balance()
        history = await bankroll_repo.get_history(limit=5)

    pnl_text = ""
    if history:
        total_pnl = sum(h.pnl or 0 for h in history)
        pnl_sign = "+" if total_pnl >= 0 else ""
        pnl_text = f"\nRecent PnL: {pnl_sign}{total_pnl:.2f}"

    text = (
        f"*Bankroll Status*\n\n"
        f"Current Balance: *${balance:.2f}*\n"
        f"{pnl_text}\n\n"
        f"Use the buttons below for more details."
    )

    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=get_bankroll_keyboard(),
    )
