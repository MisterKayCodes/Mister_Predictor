# data/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# Create the Engine (The connection to the Vault)
engine = create_async_engine("sqlite+aiosqlite:///./mister_predictor.db")

# The Librarian's Office (Session factory)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# The Blueprint (Base class for all Tables)
class Base(DeclarativeBase):
    pass