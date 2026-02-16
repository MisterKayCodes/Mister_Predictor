from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from bot.keyboards.user_menu import get_main_menu
from bot.keyboards.admin_menu import get_admin_menu
from config.settings import settings

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    is_admin = message.from_user.id in settings.admin_id_list
    menu = get_admin_menu() if is_admin else get_main_menu()

    await message.answer(
        "Welcome to *Mister Predictor*\n\n"
        "Your Football Intelligence & Value Detection System.\n\n"
        "I analyze EPL matches, detect value opportunities, "
        "and deliver data-driven betting signals.\n\n"
        "Use the menu below to navigate.",
        parse_mode="Markdown",
        reply_markup=menu,
    )


@router.message(Command("help"))
@router.message(F.text == "Help")
async def cmd_help(message: Message):
    is_admin = message.from_user.id in settings.admin_id_list

    text = (
        "*Mister Predictor - Commands*\n\n"
        "*Signals* - View today's betting signals\n"
        "*Bankroll* - Check your bankroll status\n"
        "*Browse Data* - View matches, standings, odds\n"
        "*Performance* - View prediction stats\n"
        "*Help* - Show this message\n"
    )

    if is_admin:
        text += (
            "\n*Admin Commands:*\n"
            "*Admin: Update Data* - Force data refresh\n"
            "*Admin: Run Analysis* - Run signal pipeline\n"
            "*Admin: Risk Settings* - Change risk profile\n"
            "*Admin: Status* - System health check\n"
        )

    await message.answer(text, parse_mode="Markdown")
