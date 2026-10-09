from __future__ import annotations

from typing import Any, Protocol


class DiscoveryAdapter(Protocol):
    """Normalized CARBON° discovery seam.

    External search engines or marketplace feeds must normalize results into
    CARBON° listing-shaped records before the UI sees them. The frontend does
    not need provider-specific code.
    """

    name: str
    external_search_connected: bool
    external_marketplace_connected: bool

    def search(self, query: str, listings: list[dict[str, Any]]) -> list[dict[str, Any]]: ...
    def describe(self) -> dict[str, Any]: ...


class LocalDiscoveryAdapter:
    name = "LOCAL_CARBON_MARKET"
    external_search_connected = False
    external_marketplace_connected = False

    def search(self, query: str, listings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        q = (query or "").strip().casefold()
        if not q:
            return listings
        fields = ("title", "description", "seller_intent", "negotiability")
        return [
            listing for listing in listings
            if any(q in str(listing.get(field) or "").casefold() for field in fields)
        ]

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "external_search_connected": self.external_search_connected,
            "external_marketplace_connected": self.external_marketplace_connected,
            "result_contract": "CARBON_LISTING_V1",
            "integration_rule": (
                "External providers normalize into CARBON_LISTING_V1; "
                "provider-specific discovery must not leak into marketplace UI state."
            ),
            "remaining_choice": (
                "Select search engine and/or external marketplace providers, "
                "then supply a DiscoveryAdapter implementation."
            ),
        }
