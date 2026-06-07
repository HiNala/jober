from __future__ import annotations

import uuid
from dataclasses import dataclass

from jober_api.models.enums import PlanTier


@dataclass(frozen=True)
class AuthContext:
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    plan: PlanTier
