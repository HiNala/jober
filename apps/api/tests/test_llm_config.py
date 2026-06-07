import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_llm_config_exposes_provider_and_models(client: AsyncClient) -> None:
    response = await client.get("/api/llm/config")
    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"]
    assert payload["default_model"]
    assert isinstance(payload["models"], list)
    assert len(payload["models"]) >= 1
    assert "budget_usd" in payload
