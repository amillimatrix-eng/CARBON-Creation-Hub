"""FORX prospect staging: one logical store, immutable base + bounded delta segments.

The legacy overdrive/forx_prospect_buffer.json is preserved as the base snapshot.
New observations/upserts are stored in bounded immutable delta files. A small
manifest is the conflict/version point. This avoids rewriting the >1 MiB base
for every append while preserving exact-source-key identity and readback.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_MANIFEST = Path("overdrive/forx_staging/manifest.json")


def canonical_source_key(record: dict) -> str:
    key = str(record.get("source_key") or "").strip()
    if key:
        return key
    source = str(record.get("source") or "").strip()
    if source.startswith(("http://", "https://")):
        return "url:" + source
    if ":" in source:
        return source
    return "source:" + source


def normalize_record(record: dict) -> dict:
    result = dict(record)
    result["source_key"] = canonical_source_key(result)
    if not any(
        result.get(field)
        for field in ("source_observed_at", "published", "source_updated", "freshness_state")
    ):
        result["freshness_state"] = "UNKNOWN"
    return result


def _json_bytes(value) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def git_blob_sha(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("utf-8")
    return hashlib.sha1(header + raw).hexdigest()


def load_manifest(root: Path | str, manifest_path: Path = DEFAULT_MANIFEST) -> dict:
    return json.loads((Path(root) / manifest_path).read_text(encoding="utf-8"))


def _validated_json(root: Path, descriptor: dict) -> dict:
    path = root / descriptor["path"]
    raw = path.read_bytes()
    expected = descriptor.get("git_blob_sha")
    if expected and git_blob_sha(raw) != expected:
        raise ValueError(f"blob hash mismatch: {descriptor['path']}")
    return json.loads(raw)


def read_current(root: Path | str, manifest_path: Path = DEFAULT_MANIFEST) -> list[dict]:
    root = Path(root)
    manifest = load_manifest(root, manifest_path)
    base = _validated_json(root, manifest["base_snapshot"])
    raw_base = list(base.get("candidates", []))
    if len(raw_base) != manifest["base_snapshot"]["raw_candidate_count"]:
        raise ValueError("base candidate count mismatch")

    current: dict[str, dict] = {}
    order: list[str] = []

    def apply(records):
        for candidate in records:
            record = normalize_record(candidate)
            key = record["source_key"]
            if key not in current:
                order.append(key)
            current[key] = record

    apply(raw_base)
    for segment in manifest.get("segments", []):
        body = _validated_json(root, segment)
        apply(body.get("records", []))

    records = [current[key] for key in order]
    expected = manifest.get("current_unique_source_keys")
    if expected is not None and len(records) != expected:
        raise ValueError(f"logical source-key count mismatch: {len(records)} != {expected}")
    if any(
        not any(r.get(f) for f in ("source_observed_at", "published", "source_updated", "freshness_state"))
        for r in records
    ):
        raise ValueError("current logical readback contains implicit freshness")
    return records


def append_upsert_batch(
    root: Path | str,
    records: list[dict],
    *,
    batch_id: str,
    expected_manifest_version: int,
    manifest_path: Path = DEFAULT_MANIFEST,
) -> dict:
    """Local contract used by writers/tests.

    A Git-backed writer follows the same semantics: create an immutable bounded
    delta, then update only the small manifest with stale-version protection.
    """
    root = Path(root)
    manifest_file = root / manifest_path
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    normalized = [normalize_record(r) for r in records]
    keys = [r["source_key"] for r in normalized]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate source key inside batch")

    existing = next((s for s in manifest.get("segments", []) if s.get("batch_id") == batch_id), None)
    if existing:
        body = _validated_json(root, existing)
        if body.get("records") != normalized:
            raise ValueError("batch_id collision with different payload")
        return {
            "status": "IDEMPOTENT",
            "manifest_version": manifest["manifest_version"],
            "segment": existing,
        }

    if manifest["manifest_version"] != expected_manifest_version:
        raise ValueError("stale manifest version")

    before = {r["source_key"] for r in read_current(root, manifest_path)}
    seq = int(manifest.get("next_segment_sequence", 1))
    safe_batch = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in batch_id)[:80]
    rel = f"overdrive/forx_staging/delta-{seq:04d}-{safe_batch}.json"
    body = {
        "schema_version": "2.0",
        "logical_store": "FORX_PROSPECT_STAGING",
        "segment_kind": "APPEND_UPSERT",
        "segment_sequence": seq,
        "batch_id": batch_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "records": normalized,
    }
    raw = _json_bytes(body)
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise ValueError("delta path already exists")
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(raw)
    os.replace(tmp, path)

    segment = {
        "path": rel,
        "git_blob_sha": git_blob_sha(raw),
        "count": len(normalized),
        "batch_id": batch_id,
        "source_keys": keys,
        "record_ids": [r.get("id") for r in normalized],
    }
    after = before | set(keys)
    manifest.setdefault("segments", []).append(segment)
    manifest["manifest_version"] += 1
    manifest["next_segment_sequence"] = seq + 1
    manifest["current_unique_source_keys"] = len(after)
    manifest["gross_observation_versions"] = int(
        manifest.get("gross_observation_versions", len(before))
    ) + len(normalized)
    manifest["last_updated"] = datetime.now(timezone.utc).isoformat()

    mtmp = manifest_file.with_suffix(manifest_file.suffix + ".tmp")
    mtmp.write_bytes(_json_bytes(manifest))
    os.replace(mtmp, manifest_file)

    return {
        "status": "APPENDED",
        "manifest_version": manifest["manifest_version"],
        "logical_before": len(before),
        "logical_after": len(after),
        "new_source_keys": len(set(keys) - before),
        "upserts": len(set(keys) & before),
        "segment": segment,
    }
