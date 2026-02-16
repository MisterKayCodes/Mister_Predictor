from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_menu() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Signals"), KeyboardButton(text="Bankroll")],
            [KeyboardButton(text="Browse Data"), KeyboardButton(text="Performance")],
            [KeyboardButton(text="Help")],
            [KeyboardButton(text="Admin: Update Data"), KeyboardButton(text="Admin: Run Analysis")],
            [KeyboardButton(text="Admin: Risk Settings"), KeyboardButton(text="Admin: Status")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )
    return keyboard


def get_risk_profile_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Conservative", callback_data="risk:conservative"),
                InlineKeyboardButton(text="Balanced", callback_data="risk:balanced"),
                InlineKeyboardButton(text="Aggressive", callback_data="risk:aggressive"),
            ],
        ]
    )
