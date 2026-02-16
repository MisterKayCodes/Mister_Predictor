from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config.settings import settings

engine = create_async_engine(settings.db_url, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def init_db():
    from data.models.team import Team
    from data.models.match import Match
    from data.models.odds import Odds
    from data.models.signal import Signal
    from data.models.bankroll import BankrollHistory
    from data.models.pattern_stat import PatternStat
    from data.models.standing_snapshot import StandingSnapshot

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
