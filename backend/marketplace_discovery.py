from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Protocol
from urllib.parse import quote, urlsplit, urlunsplit


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


class DiscoveryUnavailableError(RuntimeError):
    """Shared Search cannot be used; callers must not silently downgrade."""


class UnavailableDiscoveryAdapter:
    name = "INTENT_ENGINE_UNAVAILABLE"
    external_search_connected = False
    external_marketplace_connected = False

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "integration_state": "UNCONFIGURED",
            "intent_endpoint_configured": False,
            "external_search_connected": False,
            "external_marketplace_connected": False,
            "fallback_policy": "FAIL_CLOSED_NO_KEYWORD_ONLY_FALLBACK",
        }

    def search_with_metadata(
        self, query: str, listings: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        if not (query or "").strip():
            return listings, {
                **self.describe(),
                "integration_state": "BROWSE_NO_QUERY",
                "engine_invoked": False,
            }
        raise DiscoveryUnavailableError(
            "Shared CARBON° Search intent endpoint is not configured."
        )

    def search(self, query: str, listings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        records, _metadata = self.search_with_metadata(query, listings)
        return records


class IntentEngineDiscoveryAdapter:
    """Invoke the shared CARBON° Search / INTELLAGENT API for public listings."""

    name = "CARBON_INTENT_ENGINE"
    external_search_connected = False
    external_marketplace_connected = False
    max_candidates = 100

    def __init__(self, intent_url: str, client_token: str, timeout: float = 8.0):
        self.intent_url = (intent_url or "").strip()
        self.client_token = (client_token or "").strip()
        self.timeout = timeout
        parsed = urlsplit(self.intent_url) if self.intent_url else None
        self._url_valid = bool(
            parsed
            and parsed.scheme == "https"
            and parsed.netloc
            and parsed.path.rstrip("/") == "/api/search/intent"
            and not parsed.query
            and not parsed.fragment
        )
        self._valid_config = self._url_valid and bool(self.client_token)
        if self._url_valid and parsed is not None:
            sessions_path = parsed.path.rstrip("/").rsplit("/", 1)[0] + "/sessions"
            self.sessions_url = urlunsplit((parsed.scheme, parsed.netloc, sessions_path, "", ""))
        else:
            self.sessions_url = ""

    @classmethod
    def from_env(cls) -> "IntentEngineDiscoveryAdapter | None":
        endpoint = os.getenv("CARBON_SEARCH_INTENT_URL", "").strip()
        token = os.getenv("CARBON_SEARCH_CLIENT_TOKEN", "").strip()
        return cls(endpoint, token) if endpoint or token else None

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "integration_state": (
                "CONFIGURED_UNPROBED" if self._valid_config else "INVALID_CONFIGURATION"
            ),
            "intent_endpoint_configured": self._url_valid,
            "client_token_configured": bool(self.client_token),
            "external_search_connected": False,
            "external_marketplace_connected": False,
            "intent_contract": "CARBON_SEARCH_INTENT_V1",
            "surface": "client",
            "candidate_pool_limit": self.max_candidates,
            "fallback_policy": "FAIL_CLOSED_NO_KEYWORD_ONLY_FALLBACK",
            "note": (
                "Configuration alone does not prove availability; a query is verified only "
                "after intent response and session readback."
            ),
        }

    @staticmethod
    def _public_candidate(listing: dict[str, Any]) -> dict[str, Any] | None:
        listing_id = str(listing.get("id") or "").strip()
        title = str(listing.get("title") or "").strip()
        if not listing_id or not title:
            return None
        attributes = {}
        for field in (
            "price_minor", "currency", "seller_intent", "negotiability",
            "min_bond_minor", "max_considered_bond_minor",
            "min_at_risk_bps", "max_at_risk_bps", "status",
        ):
            if field in listing:
                attributes[field] = listing[field]
        return {
            "candidate_id": f"carbon-marketplace:{listing_id}",
            "title": title,
            "summary": str(listing.get("description") or "")[:4000],
            "entity_id": listing_id,
            "entity_type": "MARKETPLACE_OFFER",
            "attributes": attributes,
            "source": "CARBON° Marketplace public listing",
            "source_type": "CARBON_MARKETPLACE_PUBLIC_LISTING",
            "visibility": "CARBON_MARKETPLACE",
            "evidence_pointer": f"/api/carbon/listings/{quote(listing_id, safe='')}",
            "action": {"name": "OPEN_MARKETPLACE_LISTING", "listing_id": listing_id},
        }

    def _request_json(self, request: urllib.request.Request) -> dict[str, Any]:
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
            payload = json.loads(raw.decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            raise DiscoveryUnavailableError(
                "Shared CARBON° Search request or readback failed."
            ) from exc
        if not isinstance(payload, dict):
            raise DiscoveryUnavailableError("Shared CARBON° Search returned an invalid response.")
        return payload

    def search_with_metadata(
        self, query: str, listings: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        query = (query or "").strip()
        if not query:
            return listings, {
                **self.describe(),
                "integration_state": "BROWSE_NO_QUERY",
                "engine_invoked": False,
            }
        if not self._valid_config:
            raise DiscoveryUnavailableError(
                "A valid HTTPS CARBON_SEARCH_INTENT_URL ending in /api/search/intent and "
                "CARBON_SEARCH_CLIENT_TOKEN are required."
            )
        if len(query) > 1200:
            raise DiscoveryUnavailableError("Search query exceeds the shared intent contract limit.")

        candidates: list[dict[str, Any]] = []
        candidate_to_listing: dict[str, dict[str, Any]] = {}
        for listing in listings:
            candidate = self._public_candidate(listing)
            if candidate is not None:
                candidates.append(candidate)
                candidate_to_listing[candidate["candidate_id"]] = listing
        candidate_pool_count = len(candidates)
        truncated = candidate_pool_count > self.max_candidates
        candidates = candidates[: self.max_candidates]
        candidate_to_listing = {
            c["candidate_id"]: candidate_to_listing[c["candidate_id"]]
            for c in candidates
        }
        if not candidates:
            return [], {
                **self.describe(),
                "integration_state": "NO_CANDIDATES",
                "engine_invoked": False,
                "intent_status": "HOLD",
                "result_count": 0,
                "candidate_count_submitted": 0,
                "candidate_pool_truncated": False,
            }

        request_payload = {
            "query": query,
            "limit": min(50, len(candidates)),
            "surface": "client",
            "requested_scopes": ["CARBON_MARKETPLACE"],
            "candidates": candidates,
            "allow_pivots": False,
            "max_pivots": 0,
            "provider_mode": "AUTO",
        }
        post_request = urllib.request.Request(
            self.intent_url,
            data=json.dumps(request_payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-CARBON-Client": self.client_token,
            },
            method="POST",
        )
        intent_response = self._request_json(post_request)
        session_id = intent_response.get("session_id")
        if not isinstance(session_id, str) or not session_id.strip():
            raise DiscoveryUnavailableError(
                "Shared CARBON° Search did not return a session identifier."
            )
        session_request = urllib.request.Request(
            f"{self.sessions_url}/{quote(session_id, safe='')}",
            headers={
                "Accept": "application/json",
                "X-CARBON-Client": self.client_token,
            },
            method="GET",
        )
        session = self._request_json(session_request)
        session_candidates = session.get("candidates")
        if not isinstance(session_candidates, list):
            raise DiscoveryUnavailableError(
                "Shared CARBON° Search session readback did not include ranked candidates."
            )

        ordered: list[dict[str, Any]] = []
        seen: set[str] = set()
        for outcome in session_candidates:
            if not isinstance(outcome, dict):
                continue
            candidate_id = outcome.get("candidate_id")
            if candidate_id in candidate_to_listing and candidate_id not in seen:
                ordered.append(candidate_to_listing[candidate_id])
                seen.add(candidate_id)

        metadata = {
            **self.describe(),
            "integration_state": "QUERY_VERIFIED",
            "engine_invoked": True,
            "intent_session_id": session_id,
            "intent_status": intent_response.get("status", session.get("status", "UNKNOWN")),
            "candidate_pool_count": candidate_pool_count,
            "candidate_count_submitted": len(candidates),
            "candidate_pool_truncated": truncated,
            "result_count": len(ordered),
        }
        return ordered, metadata

    def search(self, query: str, listings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        records, _metadata = self.search_with_metadata(query, listings)
        return records
