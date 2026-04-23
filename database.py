import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./db.sqlite3")

connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith('sqlite') else {}

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False, future=True, connect_args=connect_args)

AsyncSessionLokal = async_sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLokal() as db:
        yield db


async def init_db():
    import models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
