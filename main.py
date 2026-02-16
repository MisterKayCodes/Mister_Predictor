import asyncio
import logging
from utils.logging import setup_logging
from config.settings import settings
from data.database import init_db, AsyncSessionLocal
from data.repositories.bankroll_repo import BankrollRepository
from bot.bot_factory import create_bot, create_dispatcher
from services.scheduling.daily_runner import DailyRunner
from apscheduler.schedulers.asyncio import AsyncIOScheduler

setup_logging()
logger = logging.getLogger("main")


async def initialize_database():
    logger.info("Initializing database tables...")
    await init_db()

    async with AsyncSessionLocal() as session:
        bankroll_repo = BankrollRepository(session)
        await bankroll_repo.initialize_if_empty()
        await session.commit()

    logger.info("Database initialized successfully")


async def scheduled_daily_run():
    logger.info("Scheduled daily cycle triggered")
    runner = DailyRunner()
    try:
        stats = await runner.run_daily_cycle()
        logger.info(f"Daily cycle results: {stats}")
    except Exception as e:
        logger.error(f"Daily cycle failed: {e}")


def setup_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        scheduled_daily_run,
        "cron",
        hour=settings.DAILY_RUN_HOUR,
        minute=settings.DAILY_RUN_MINUTE,
        id="daily_intelligence_cycle",
        replace_existing=True,
    )
    return scheduler


async def main():
    logger.info("=" * 50)
    logger.info("MISTER PREDICTOR - Starting Up")
    logger.info("Football Intelligence & Value Detection System")
    logger.info("=" * 50)

    await initialize_database()

    token = settings.BOT_TOKEN.get_secret_value()
    if not token:
        logger.error(
            "BOT_TOKEN not set. Please set the BOT_TOKEN environment variable "
            "or add it to .env file."
        )
        logger.info("Running in headless mode (no Telegram). Scheduler active.")

        scheduler = setup_scheduler()
        scheduler.start()

        try:
            while True:
                await asyncio.sleep(3600)
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
        return

    bot = create_bot(token)
    dp = create_dispatcher()

    scheduler = setup_scheduler()
    scheduler.start()
    logger.info(
        f"Scheduler started - daily cycle at "
        f"{settings.DAILY_RUN_HOUR:02d}:{settings.DAILY_RUN_MINUTE:02d} UTC"
    )

    logger.info("Bot is now polling for messages...")
    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()
        await bot.session.close()
        logger.info("Bot shut down cleanly")


if __name__ == "__main__":
    asyncio.run(main())
