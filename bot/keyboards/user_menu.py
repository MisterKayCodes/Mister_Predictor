from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Signals"), KeyboardButton(text="Bankroll")],
            [KeyboardButton(text="Browse Data"), KeyboardButton(text="Performance")],
            [KeyboardButton(text="Help")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )
    return keyboard


def get_signal_filter_keyboard(active: str = "matchday") -> InlineKeyboardMarkup:
    filters = [
        ("Next Matchday", "sig_filter:matchday"),
        ("Next 3 Days", "sig_filter:3days"),
        ("This Week", "sig_filter:week"),
        ("All Upcoming", "sig_filter:all"),
    ]

    buttons = []
    for label, cb_data in filters:
        key = cb_data.split(":")[1]
        display = f"[ {label} ]" if key == active else label
        buttons.append(InlineKeyboardButton(text=display, callback_data=cb_data))

    return InlineKeyboardMarkup(
        inline_keyboard=[
            buttons[:2],
            buttons[2:],
        ]
    )


def get_browse_data_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Upcoming Matches", callback_data="browse:upcoming"),
                InlineKeyboardButton(text="Recent Results", callback_data="browse:results"),
            ],
            [
                InlineKeyboardButton(text="League Standings", callback_data="browse:standings"),
                InlineKeyboardButton(text="Live Odds", callback_data="browse:odds"),
            ],
        ]
    )


def get_signal_details_keyboard(signal_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="View Full Analysis",
                    callback_data=f"signal_detail:{signal_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Mark as Placed",
                    callback_data=f"signal_placed:{signal_id}",
                ),
            ],
        ]
    )


def get_bankroll_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="History", callback_data="bankroll_history"),
                InlineKeyboardButton(text="Reset", callback_data="bankroll_reset"),
            ],
        ]
    )


def get_performance_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Pattern Stats", callback_data="perf_patterns"),
                InlineKeyboardButton(text="Recent Results", callback_data="perf_recent"),
            ],
        ]
    )
