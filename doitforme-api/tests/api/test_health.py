async def test_health_endpoint_returns_success_envelope(async_client):
    response = await async_client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ok"
    assert body["error"] is None
    assert "timestamp" in body


async def test_ready_endpoint_returns_success_envelope(async_client):
    response = await async_client.get("/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ready"
    assert body["error"] is None
    assert "timestamp" in body


async def test_api_v1_root_returns_success_envelope(async_client):
    response = await async_client.get("/api/v1")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["message"] == "DoItForMe API v1"
