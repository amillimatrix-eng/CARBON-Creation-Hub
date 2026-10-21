import hashlib
import json
import sqlite3

import pytest

from overdrive.forx_stage1_runtime import app as runtime


def _node(key, country, category):
    return {
        "source_record_id": key,
        "name": key,
        "latitude": 1.0,
        "longitude": 2.0,
        "country": country,
        "category": category,
        "source": "TEST",
    }


def test_disk_backed_selector_and_streamed_partition_hashes(tmp_path):
    store = runtime.create_node_store(str(tmp_path / "store-"))
    conn = sqlite3.connect(store)
    rows = [
        _node("a", "ZA", "city"),
        _node("b", "ZA", "landmark"),
        _node("c", "US", "city"),
        _node("d", "US", "city"),
        _node("e", "ZA", "city"),
        _node("f", "ZA", "landmark"),
    ]
    try:
        for i, node in enumerate(rows, 1):
            conn.execute(
                "INSERT OR IGNORE INTO nodes (ck,country,category,source_record_id,sequence,payload) "
                "VALUES (?,?,?,?,?,?)",
                (f"key-{i}", node["country"], node["category"], node["source_record_id"],
                 i, json.dumps(node, separators=(",", ":"), sort_keys=True)),
            )
        conn.commit()
    finally:
        conn.close()

    output_dir = tmp_path / "parts"
    output_dir.mkdir()
    result = runtime.write_streamed_partitions(
        store, 5, 2, str(output_dir), "run-test", "checkpoint-test", "sequence"
    )
    try:
        assert result["selected_count"] == 5
        assert [part["count"] for part in result["parts"]] == [2, 2, 1]
        emitted = []
        for part in result["parts"]:
            raw = open(part["path"], "rb").read()
            assert hashlib.sha256(raw).hexdigest() == part["sha256"]
            body = json.loads(raw)
            assert len(body["nodes"]) == part["count"] <= 2
            assert body["run_id"] == "run-test"
            emitted.extend(node["source_record_id"] for node in body["nodes"])
        assert emitted == ["c", "a", "b", "d", "e"]
        assert result["selection_sha256"] == hashlib.sha256("\n".join(emitted).encode()).hexdigest()
    finally:
        runtime.remove_sqlite(store)


def _write_durable_checkpoint(project_root, run_id="run-test", node_ids=("a", "b", "c"), partition_size=2):
    proof_dir = project_root / "overdrive" / "forx_50k_proof" / run_id
    proof_dir.mkdir(parents=True)
    nodes = [
        {
            "source_record_id": key,
            "name": key,
            "latitude": float(index),
            "longitude": float(index + 1),
            "country": "ZA",
            "category": "city",
            "source": "TEST",
        }
        for index, key in enumerate(node_ids)
    ]

    partition_hashes = {}
    for index, start in enumerate(range(0, len(nodes), partition_size), 1):
        body = {
            "schema_version": "2.2",
            "run_id": run_id,
            "checkpoint_id": run_id,
            "partition_index": index,
            "nodes": nodes[start:start + partition_size],
        }
        raw = json.dumps(body, separators=(",", ":"), sort_keys=True).encode("utf-8")
        (proof_dir / f"partition-{index:03d}.json").write_bytes(raw)
        partition_hashes[str(index)] = hashlib.sha256(raw).hexdigest()

    selection_sha256 = hashlib.sha256("\n".join(node_ids).encode("utf-8")).hexdigest()
    source_sha256 = "a" * 64
    partition_count = len(partition_hashes)
    manifest = {
        "schema_version": "2.2",
        "manifest_type": "FORX_PRODUCTION_MANIFEST",
        "mode": "production",
        "run_id": run_id,
        "checkpoint_id": run_id,
        "source_adapter": "geonames-cities500",
        "source": "TEST source",
        "source_url": "https://example.invalid/source.zip",
        "source_license": "CC BY 4.0",
        "source_revision": "test-revision",
        "source_file_sha256": source_sha256,
        "target": len(nodes),
        "partition_size": partition_size,
        "partition_count": partition_count,
        "partition_hashes": partition_hashes,
        "selected_count": len(nodes),
        "selection_sha256": selection_sha256,
        "source_cursor_start": 0,
        "source_cursor_next": len(nodes),
        "cumulative_unique_count_snapshot": len(nodes),
        "raw_rows_ingested": len(nodes),
        "rows_rejected": 0,
        "duplicates_removed": 0,
        "country_count": 1,
        "category_count": 1,
        "source_distribution": {"TEST source": len(nodes)},
        "website_domain_bearing_count": 0,
        "started_at": "2026-10-21T00:00:00+00:00",
        "completed_at": "2026-10-21T00:01:00+00:00",
    }
    status_doc = {
        "status": "COMPLETE",
        "phase": "RUNTIME_OUTPUT_READY_NOT_DURABLY_VERIFIED",
        "mode": "production",
        "run_id": run_id,
        "node_count": len(nodes),
        "partition_count": partition_count,
        "partition_size": partition_size,
        "target": len(nodes),
        "source_adapter": "geonames-cities500",
        "country_count": 1,
        "category_count": 1,
        "errors": [],
    }
    durable_receipt = {
        "receipt_type": "FORX_DURABLE_RUNTIME_PERSISTENCE_READBACK",
        "status": "PASS_DURABLE_PARTITIONS_VERIFIED",
        "run_id": run_id,
        "source_file_sha256": source_sha256,
        "selection_sha256": selection_sha256,
        "target": len(nodes),
        "exact_node_count_readback": len(nodes),
        "unique_source_record_id_count": len(nodes),
        "coordinate_backed_count": len(nodes),
        "partition_count": partition_count,
        "partition_size": partition_size,
        "partition_hashes_verified": True,
        "all_partition_hashes": partition_hashes,
    }
    (proof_dir / "status.json").write_text(json.dumps(status_doc), encoding="utf-8")
    (proof_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (proof_dir / "durable-readback-receipt.json").write_text(json.dumps(durable_receipt), encoding="utf-8")
    return proof_dir


def test_restore_validates_and_rehydrates_durable_checkpoint(tmp_path):
    proof_dir = _write_durable_checkpoint(tmp_path)
    restored = runtime.restore_durable_checkpoint(
        "run-test", "run-test", 3, 2, "geonames-cities500", project_root=tmp_path
    )

    assert restored["status"] == "COMPLETE"
    assert restored["phase"] == "DURABLE_CHECKPOINT_RESTORED"
    assert restored["restored_from_checkpoint"] is True
    assert restored["node_count"] == 3
    assert [part["count"] for part in restored["partitions"]] == [2, 1]
    assert restored["receipt"]["status"] == "PRODUCTION_RUNTIME_RESTORED_FROM_DURABLE_CHECKPOINT"
    for part in restored["partitions"]:
        raw = open(part["path"], "rb").read()
        assert hashlib.sha256(raw).hexdigest() == part["sha256"]
    assert (proof_dir / "manifest.json").is_file()


def test_restore_fails_closed_on_partition_byte_hash_mismatch(tmp_path):
    proof_dir = _write_durable_checkpoint(tmp_path)
    (proof_dir / "partition-001.json").write_bytes(b"{}")

    with pytest.raises(ValueError, match="partition 1 SHA-256 mismatch"):
        runtime.restore_durable_checkpoint(
            "run-test", "run-test", 3, 2, "geonames-cities500", project_root=tmp_path
        )


def test_restore_fails_closed_on_duplicate_source_record_ids(tmp_path):
    _write_durable_checkpoint(tmp_path, node_ids=("a", "b", "b"))

    with pytest.raises(ValueError, match="duplicate source_record_id"):
        runtime.restore_durable_checkpoint(
            "run-test", "run-test", 3, 2, "geonames-cities500", project_root=tmp_path
        )


def test_missing_durable_checkpoint_allows_new_run(tmp_path):
    assert runtime.restore_durable_checkpoint(
        "new-run", "new-run", 3, 2, "geonames-cities500", project_root=tmp_path
    ) is None


def test_restore_rejects_checkpoint_for_different_target(tmp_path):
    _write_durable_checkpoint(tmp_path)

    with pytest.raises(ValueError, match="status node_count mismatch"):
        runtime.restore_durable_checkpoint(
            "run-test", "run-test", 4, 2, "geonames-cities500", project_root=tmp_path
        )
