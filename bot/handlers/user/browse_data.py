from aiogram import Router, F
from aiogram.types import Message
from bot.keyboards.user_menu import get_browse_data_keyboard

router = Router()


@router.message(F.text == "Browse Data")
async def browse_data(message: Message):
    await message.answer(
        "*Browse EPL Data*\n\n"
        "Choose what you'd like to see:",
        parse_mode="Markdown",
        reply_markup=get_browse_data_keyboard(),
    )
