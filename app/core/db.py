from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from .config import settings

async_engine = create_async_engine(url=settings.DATABASE_URL, echo=True)


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
