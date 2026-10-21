import hashlib
import json
import sqlite3

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
