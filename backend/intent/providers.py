from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from .models import CandidateInput, EntityType, SearchScope


class JsonHttpExternalProvider:
    """Provider-neutral JSON-over-HTTP retrieval adapter.

    Expected response: {"results": [{candidate fields...}]}. No provider semantics are
    embedded in Search. Configuration comes from deployment environment.
    """

    name = "json-http-external"

    def __init__(self, endpoint: str, token: str | None = None, timeout: float = 8.0):
        self.endpoint = endpoint
        self.token = token
        self.timeout = timeout

    @classmethod
    def from_env(cls) -> "JsonHttpExternalProvider | None":
        endpoint = os.getenv("CARBON_SEARCH_EXTERNAL_URL", "").strip()
        if not endpoint:
            return None
        return cls(endpoint, os.getenv("CARBON_SEARCH_EXTERNAL_TOKEN"))

    def search(self, query: str, limit: int) -> list[CandidateInput]:
        body = json.dumps({"query": query, "limit": limit}).encode("utf-8")
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = urllib.request.Request(self.endpoint, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            raise RuntimeError(f"external retrieval unavailable: {exc}") from exc
        results = payload.get("results", []) if isinstance(payload, dict) else []
        out: list[CandidateInput] = []
        for idx, item in enumerate(results[:limit]):
            if not isinstance(item, dict):
                continue
            out.append(CandidateInput(
                candidate_id=str(item.get("candidate_id") or item.get("id") or f"external:{idx}"),
                title=str(item.get("title") or item.get("name") or "External result"),
                summary=str(item.get("summary") or item.get("snippet") or ""),
                entity_id=item.get("entity_id"),
                entity_type=EntityType(item.get("entity_type", "UNKNOWN")) if item.get("entity_type") in EntityType._value2member_map_ else EntityType.UNKNOWN,
                attributes=item.get("attributes") or {},
                source=str(item.get("source") or self.endpoint),
                source_type=str(item.get("source_type") or "EXTERNAL_PROVIDER"),
                source_timestamp=item.get("source_timestamp"),
                visibility=SearchScope.PUBLIC,
                evidence_pointer=item.get("evidence_pointer") or item.get("url"),
                action=item.get("action"),
            ))
        return out


class FileMarketplaceProvider:
    """Consumes a governed Marketplace signal projection when one is configured."""

    name = "file-marketplace"

    def __init__(self, path: Path):
        self.path = Path(path)

    @classmethod
    def from_env(cls) -> "FileMarketplaceProvider | None":
        raw = os.getenv("AMX_MARKETPLACE_SIGNAL_PATH", "").strip()
        return cls(Path(raw)) if raw else None

    def search(self, query: str, limit: int) -> list[CandidateInput]:
        if not self.path.exists():
            raise RuntimeError("marketplace signal projection unavailable")
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        records = payload.get("records", payload.get("signals", [])) if isinstance(payload, dict) else payload
        if not isinstance(records, list):
            raise RuntimeError("marketplace signal projection invalid")
        tokens = {t for t in query.casefold().split() if len(t) > 1}
        ranked: list[tuple[int, dict[str, Any]]] = []
        for raw in records:
            if not isinstance(raw, dict):
                continue
            hay = json.dumps(raw, ensure_ascii=False).casefold()
            score = sum(1 for t in tokens if t in hay)
            if score:
                ranked.append((score, raw))
        ranked.sort(key=lambda x: -x[0])
        out: list[CandidateInput] = []
        for idx, (_, raw) in enumerate(ranked[:limit]):
            out.append(CandidateInput(
                candidate_id=str(raw.get("candidate_id") or raw.get("listing_id") or raw.get("signal_id") or f"market:{idx}"),
                title=str(raw.get("title") or raw.get("name") or raw.get("intent") or "Marketplace signal"),
                summary=str(raw.get("summary") or raw.get("intent") or ""),
                entity_id=raw.get("entity_id"),
                entity_type=EntityType.MARKETPLACE_OFFER,
                attributes=raw.get("attributes") or raw,
                source=str(self.path),
                source_type="MARKETPLACE_SIGNAL",
                source_timestamp=raw.get("updated_at") or raw.get("created_at"),
                visibility=SearchScope.CARBON_MARKETPLACE,
                evidence_pointer=str(raw.get("evidence_pointer") or self.path),
                action=raw.get("action"),
            ))
        return out
