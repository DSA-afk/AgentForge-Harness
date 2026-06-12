import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_check(client):

    response = await client.get("/health")

    assert response.status_code == 200
    print("✅ 测试通过！框架跑通了！")
