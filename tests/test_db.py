import pytest


@pytest.mark.asyncio
async def test_tenant_a_sees_only_own(client):
    result = await client.get(
        "/health/document",
        headers={
            "X-Tenant-Id": "tenant-a"
        }
    )

    data = result.json()["result"]

    assert result.status_code == 200
    assert len(data) >= 1
    assert any(d["id"] == "doc-a" for d in data)
    assert all(
        d["tenant_id"] == "tenant-a"
        for d in data
    )
    print("✅ 测试通过！")


@pytest.mark.asyncio
async def test_tenant_b_sees_only_own(client):
    result = await client.get(
        "/health/document",
        headers={
            "X-Tenant-Id": "tenant-b"
        }
    )

    data = result.json()["result"]

    assert result.status_code == 200
    assert len(data) >= 1
    assert any(d["id"] == "doc-b" for d in data)
    assert all(
        d["tenant_id"] == "tenant-b"
        for d in data
    )
    print("✅ 测试通过！")


@pytest.mark.asyncio
async def test_no_tenant_returns_empty(client):
    result = await client.get(
        "/health/document"
    )

    data = result.json()["result"]

    assert result.status_code == 200
    assert data == []
    print("✅ 测试通过！")
