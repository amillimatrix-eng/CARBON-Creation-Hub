from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel, Field


class MarketplaceIntentSignal(BaseModel):
    signal_id: str
    kind: str = Field(pattern="^(DEMAND|SUPPLY|AVAILABILITY|OUTCOME)$")
    canonical_entity_id: str | None = None
    text: str = ""
    attributes: dict[str, Any] = Field(default_factory=dict)
    source: str
    observed_at: str
    visibility: str = "CARBON_MARKETPLACE"


class MarketplaceSearchAdapter(Protocol):
    """Search-owned interface for Market-of-Intent signals."""

    def search_intent(self, query: str, limit: int) -> list[MarketplaceIntentSignal]: ...
