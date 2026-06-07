from __future__ import annotations

FIT_LANE_VARIANTS: dict[str, str] = {
    "ai product": "AI Product",
    "ai platform": "AI Product",
    "product eng": "AI Product",
    "founding full-stack": "Founding Full-Stack",
    "full-stack": "Founding Full-Stack",
    "frontend-design": "Frontend-Design",
    "frontend": "Frontend-Design",
    "fde-solutions": "FDE-Solutions",
    "fde": "FDE-Solutions",
    "devtools-security": "Devtools-Security",
    "devtools": "Devtools-Security",
    "security": "Devtools-Security",
    "applied ml": "AI Product",
}


def map_fit_lane_to_variant(fit_lane: str | None) -> str:
    if not fit_lane:
        return "canonical"
    key = fit_lane.strip().casefold()
    return FIT_LANE_VARIANTS.get(key, "canonical")


def match_angle_use_case(fit_lane: str | None, hook: str | None) -> str | None:
    if not fit_lane:
        return None
    lane = fit_lane.casefold()
    if "ai" in lane or "ml" in lane:
        return "AI platform role"
    if "full" in lane or "founder" in lane:
        return "Founding engineer"
    if "frontend" in lane or "design" in lane:
        return "Frontend-heavy role"
    if hook and "rag" in hook.casefold():
        return "RAG / agents role"
    return None
