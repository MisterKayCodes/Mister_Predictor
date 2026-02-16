import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from bot.handlers.user import start, signals, bankroll, performance, browse_data
from bot.handlers.admin import update_data, run_analysis, risk_control
from bot.callbacks import router as callbacks_router
from bot.middlewares.auth import AdminCheckMiddleware
from bot.middlewares.logging import LoggingMiddleware

logger = logging.getLogger(__name__)


def create_bot(token: str) -> Bot:
    return Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    dp.message.middleware(LoggingMiddleware())
    dp.message.middleware(AdminCheckMiddleware())

    dp.include_router(start.router)
    dp.include_router(signals.router)
    dp.include_router(bankroll.router)
    dp.include_router(performance.router)
    dp.include_router(browse_data.router)

    dp.include_router(update_data.router)
    dp.include_router(run_analysis.router)
    dp.include_router(risk_control.router)

    dp.include_router(callbacks_router)

    logger.info("Bot dispatcher created with all handlers registered")
    return dp
