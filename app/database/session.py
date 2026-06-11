from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .config import config
from sqlalchemy import text
from fastapi import Depends,Request

engine = create_async_engine(config.APP_DB_URL, pool_pre_ping=True, )

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db(request: Request):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(
                text("SELECT set_config('app.current_tenant', :tid, true)"),
                {'tid': request.headers.get('X-Tenant-Id') or ''}
            )
            yield session
