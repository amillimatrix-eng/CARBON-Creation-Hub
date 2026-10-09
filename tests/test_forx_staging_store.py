import hashlib
import json

import pytest

from overdrive.forx_staging_store import (
    append_upsert_batch,
    canonical_source_key,
    git_blob_sha,
    normalize_record,
    read_current,
)


def _write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _seed(tmp_path):
    base = tmp_path / "overdrive/forx_prospect_buffer.json"
    _write(
        base,
        {
            "candidates": [
                {"id": "A1", "source": "https://a.example/", "organization": "A old"},
                {"id": "B1", "source_key": "google_business:b", "source": "google_business:b", "published": "2026-10-01"},
                {"id": "A2", "source_key": "url:https://a.example/", "source": "https://a.example/", "organization": "A current"},
            ]
        },
    )
    manifest = {
        "schema_version": "2.0",
        "manifest_version": 1,
        "base_snapshot": {
            "path": "overdrive/forx_prospect_buffer.json",
            "git_blob_sha": git_blob_sha(base.read_bytes()),
            "raw_candidate_count": 3,
        },
        "segments": [],
        "current_unique_source_keys": 2,
        "gross_observation_versions": 3,
        "next_segment_sequence": 1,
    }
    _write(tmp_path / "overdrive/forx_staging/manifest.json", manifest)


def test_source_key_and_freshness_normalization():
    record = normalize_record({"source": "https://x.example/"})
    assert record["source_key"] == "url:https://x.example/"
    assert record["freshness_state"] == "UNKNOWN"
    assert canonical_source_key({"source": "google_business:abc"}) == "google_business:abc"


def test_base_readback_collapses_exact_source_duplicate_but_preserves_latest_version(tmp_path):
    _seed(tmp_path)
    records = read_current(tmp_path)
    assert len(records) == 2
    by_key = {r["source_key"]: r for r in records}
    assert by_key["url:https://a.example/"]["id"] == "A2"
    assert by_key["url:https://a.example/"]["freshness_state"] == "UNKNOWN"


def test_append_new_key_changes_logical_count_and_survives_readback(tmp_path):
    _seed(tmp_path)
    result = append_upsert_batch(
        tmp_path,
        [{"id": "C1", "source": "https://c.example/", "organization": "C"}],
        batch_id="batch-new",
        expected_manifest_version=1,
    )
    assert result["status"] == "APPENDED"
    assert result["logical_before"] == 2
    assert result["logical_after"] == 3
    assert result["new_source_keys"] == 1
    assert len(read_current(tmp_path)) == 3


def test_same_source_key_is_upsert_not_growth(tmp_path):
    _seed(tmp_path)
    result = append_upsert_batch(
        tmp_path,
        [{"id": "A3", "source": "https://a.example/", "organization": "A newest"}],
        batch_id="batch-upsert",
        expected_manifest_version=1,
    )
    assert result["upserts"] == 1
    assert result["new_source_keys"] == 0
    assert result["logical_after"] == 2
    current = {r["source_key"]: r for r in read_current(tmp_path)}
    assert current["url:https://a.example/"]["id"] == "A3"


def test_stale_manifest_rejected(tmp_path):
    _seed(tmp_path)
    append_upsert_batch(
        tmp_path,
        [{"id": "C1", "source": "https://c.example/"}],
        batch_id="batch-one",
        expected_manifest_version=1,
    )
    with pytest.raises(ValueError, match="stale manifest version"):
        append_upsert_batch(
            tmp_path,
            [{"id": "D1", "source": "https://d.example/"}],
            batch_id="batch-two",
            expected_manifest_version=1,
        )


def test_retry_same_batch_is_idempotent(tmp_path):
    _seed(tmp_path)
    payload = [{"id": "C1", "source": "https://c.example/"}]
    first = append_upsert_batch(tmp_path, payload, batch_id="batch-one", expected_manifest_version=1)
    second = append_upsert_batch(tmp_path, payload, batch_id="batch-one", expected_manifest_version=1)
    assert first["status"] == "APPENDED"
    assert second["status"] == "IDEMPOTENT"
    assert len(read_current(tmp_path)) == 3


def test_retry_same_batch_with_different_payload_fails(tmp_path):
    _seed(tmp_path)
    append_upsert_batch(
        tmp_path,
        [{"id": "C1", "source": "https://c.example/"}],
        batch_id="batch-one",
        expected_manifest_version=1,
    )
    with pytest.raises(ValueError, match="batch_id collision"):
        append_upsert_batch(
            tmp_path,
            [{"id": "C2", "source": "https://different.example/"}],
            batch_id="batch-one",
            expected_manifest_version=1,
        )


def test_segment_blob_hash_is_verified(tmp_path):
    _seed(tmp_path)
    append_upsert_batch(
        tmp_path,
        [{"id": "C1", "source": "https://c.example/"}],
        batch_id="batch-one",
        expected_manifest_version=1,
    )
    manifest = json.loads((tmp_path / "overdrive/forx_staging/manifest.json").read_text())
    delta = tmp_path / manifest["segments"][0]["path"]
    delta.write_text(delta.read_text() + " ", encoding="utf-8")
    with pytest.raises(ValueError, match="blob hash mismatch"):
        read_current(tmp_path)


def test_repository_manifest_exact_readback():
    root = __import__("pathlib").Path(__file__).resolve().parents[1]
    records = read_current(root)
    manifest = json.loads((root / "overdrive/forx_staging/manifest.json").read_text())
    keys = {r["source_key"] for r in records}
    assert len(records) == manifest["current_unique_source_keys"]
    assert len({r["id"] for r in records}) == len(records)
    assert all(
        any(r.get(field) for field in ("source_observed_at", "published", "source_updated", "freshness_state"))
        for r in records
    )
    expected = {
        "url:https://oluxconsulting.com/",
        "url:https://msassd.com/",
        "url:https://newpeakss.com/",
        "url:https://hashenconsulting.com/",
        "url:https://amani-juris.bi/",
        "url:https://nconsultea.com/",
        "url:https://sstconsultancy.bi/",
        "url:https://www.rohnproctor.com/",
        "url:https://cabinetsacofi.com/",
    }
    assert expected <= keys
