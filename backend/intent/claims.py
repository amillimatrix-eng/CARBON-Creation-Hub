from __future__ import annotations

import hashlib
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from .models import CandidateInput, EvidenceClaim, SearchScope


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def claim_id(entity_id: str, attribute: str, source: str, value: Any) -> str:
    raw = f"{entity_id}|{attribute}|{source}|{value!r}".encode("utf-8")
    return "CLM-" + hashlib.sha256(raw).hexdigest()[:20].upper()


def normalize_candidate_claims(candidate: CandidateInput) -> list[EvidenceClaim]:
    entity_id = candidate.entity_id or candidate.candidate_id
    retrieved = now_iso()
    claims: list[EvidenceClaim] = []
    for key, value in sorted(candidate.attributes.items()):
        claims.append(EvidenceClaim(
            claim_id=claim_id(entity_id, key, candidate.source, value),
            entity_id=entity_id,
            attribute=key,
            value=value,
            source=candidate.source,
            source_type=candidate.source_type,
            source_timestamp=candidate.source_timestamp,
            retrieved_at=retrieved,
            freshness_class="CURRENT" if candidate.source_timestamp else "UNKNOWN",
            authority_class="SUPPLIED" if candidate.source_type == "SUPPLIED" else "RETRIEVED",
            confidence=1.0,
            visibility=candidate.visibility,
            evidence_pointer=candidate.evidence_pointer,
        ))
    return claims


def contradiction_groups(claims: list[EvidenceClaim]) -> tuple[list[EvidenceClaim], list[dict[str, Any]]]:
    groups: dict[tuple[str, str], list[EvidenceClaim]] = defaultdict(list)
    for claim in claims:
        if claim.validity == "VALID":
            groups[(claim.entity_id, claim.attribute)].append(claim)

    contradictions: list[dict[str, Any]] = []
    replacements: dict[str, EvidenceClaim] = {}
    for (entity_id, attribute), items in groups.items():
        values = {repr(item.value) for item in items}
        if len(values) <= 1:
            continue
        group_id = "CTR-" + hashlib.sha256(f"{entity_id}|{attribute}".encode()).hexdigest()[:16].upper()
        contradictions.append({
            "group_id": group_id,
            "entity_id": entity_id,
            "attribute": attribute,
            "values": [item.value for item in items],
            "claim_ids": [item.claim_id for item in items],
            "state": "UNRESOLVED",
        })
        for item in items:
            replacements[item.claim_id] = item.model_copy(update={"contradiction_group": group_id})
    return [replacements.get(c.claim_id, c) for c in claims], contradictions


def visible_claims(claims: list[EvidenceClaim], allowed: set[SearchScope]) -> list[EvidenceClaim]:
    return [c for c in claims if c.visibility in allowed]
