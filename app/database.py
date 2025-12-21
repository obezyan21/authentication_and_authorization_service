from typing import AsyncGenerator, Annotated

from fastapi import Depends
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

engine = create_async_engine("sqlite+aiosqlite:///auth.db")

new_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
     pass

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

class DatabaseService:
    async def setup_database(self):
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
            return True
