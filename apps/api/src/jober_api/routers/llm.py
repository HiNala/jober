from fastapi import APIRouter

from jober_api.config import settings

router = APIRouter(tags=["llm"])


@router.get("/llm/config")
async def llm_config() -> dict[str, object]:
    """Expose gateway provider and selectable models for the workspace command bar."""
    models: list[dict[str, str]] = []
    seen: set[str] = set()
    for model_id, role, label in (
        (settings.llm_draft_model, "draft", "Draft"),
        (settings.llm_scoring_model, "scoring", "Scoring"),
        (settings.llm_embedding_model, "embedding", "Embeddings"),
    ):
        if model_id in seen:
            continue
        seen.add(model_id)
        models.append({"id": model_id, "role": role, "label": label})
    return {
        "provider": settings.llm_provider,
        "default_model": settings.llm_draft_model,
        "models": models,
        "budget_usd": settings.llm_monthly_budget_usd,
    }
