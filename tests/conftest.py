import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.database.session import engine


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
    ) as client:
        yield client

    await engine.dispose()  # ← 测试结束、在本循环内清空连接池
