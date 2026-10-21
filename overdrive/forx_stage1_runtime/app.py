import csv, hashlib, io, json, os, shutil, sqlite3, tempfile, threading, zipfile
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, Response

app = FastAPI(title="AMX FORX Bulk Runtime")

AUDIALA_URL = "https://huggingface.co/datasets/audiala/audiala-places/resolve/main/data/audiala-places.csv"
AUDIALA_REPO = "audiala/audiala-places"
AUDIALA_LICENSE = "CC BY 4.0"
AUDIALA_FILE_SHA256 = "e21c7e92357ea062db51445baaaef1fa45fedb24cf095b72b520199f86b2b47c"
AUDIALA_REPO_COMMIT = "e033fb7"
AUDIALA_UPDATED = "2026-09-28"

GEONAMES_URL = "https://download.geonames.org/export/dump/cities500.zip"
GEONAMES_LICENSE = "CC BY 4.0"
GEONAMES_SOURCE = "GeoNames cities500"

MODE = os.getenv("FORX_MODE", "production").strip().lower()
TARGET = int(os.getenv("FORX_TARGET", "50000" if MODE != "stage1-proof" else "1200"))
PARTITION_SIZE = int(os.getenv("FORX_PARTITION_SIZE", "1000" if MODE != "stage1-proof" else "100"))
SOURCE_ADAPTER = os.getenv(
    "FORX_SOURCE_ADAPTER",
    "geonames-cities500" if MODE != "stage1-proof" else "audiala-stage1",
)
RUN_ID = os.getenv("FORX_RUN_ID") or datetime.now(timezone.utc).strftime("forx-%Y%m%dT%H%M%SZ")
CHECKPOINT_ID = os.getenv("FORX_CHECKPOINT_ID", RUN_ID)

if TARGET < 1:
    raise RuntimeError("FORX_TARGET must be >= 1")
if PARTITION_SIZE < 1:
    raise RuntimeError("FORX_PARTITION_SIZE must be >= 1")

state = {
    "status": "STARTING",
    "phase": "STARTUP",
    "started_at": None,
    "completed_at": None,
    "node_count": 0,
    "partitions": [],
    "partition_dir": None,
    "manifest": None,
    "receipt": None,
    "errors": [],
}
lock = threading.Lock()


def norm(s):
    return "".join(ch.lower() for ch in str(s or "") if ch.isalnum())


def parse_float(v):
    try:
        return float(v)
    except Exception:
        return None


def canonical_key(name, lat, lon):
    return f"{norm(name)}|{round(float(lat), 4)}|{round(float(lon), 4)}"


def create_node_store(prefix):
    """Create a disk-backed, deduplicated node store; never keep the population in RAM."""
    fd, path = tempfile.mkstemp(prefix=prefix, suffix=".sqlite3")
    os.close(fd)
    conn = sqlite3.connect(path)
    try:
        conn.execute("PRAGMA journal_mode=OFF")
        conn.execute("PRAGMA synchronous=OFF")
        conn.execute("PRAGMA temp_store=FILE")
        conn.execute("PRAGMA cache_size=-4096")
        conn.execute(
            """
            CREATE TABLE nodes (
                ck TEXT PRIMARY KEY,
                country TEXT NOT NULL,
                category TEXT NOT NULL,
                source_record_id TEXT NOT NULL,
                sequence INTEGER NOT NULL,
                payload TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()
    return path


def remove_sqlite(path):
    """Remove a runtime-owned temporary SQLite store without failing cleanup."""
    if not path:
        return
    for candidate in (path, path + "-journal", path + "-wal", path + "-shm"):
        try:
            os.remove(candidate)
        except FileNotFoundError:
            pass


def iter_store_nodes(store_path):
    """Iterate every stored payload in source insertion order, one row at a time."""
    conn = sqlite3.connect(store_path)
    try:
        conn.execute("PRAGMA temp_store=FILE")
        conn.execute("PRAGMA cache_size=-2048")
        cursor = conn.execute("SELECT payload FROM nodes ORDER BY sequence")
        for (payload,) in cursor:
            yield json.loads(payload)
    finally:
        conn.close()


def iter_diverse_nodes(store_path, target, selection_order="sequence"):
    """Yield a stable round-robin by country/category using disk-backed SQL ordering."""
    order_column = {
        "sequence": "sequence",
        "source_record_id": "source_record_id",
    }.get(selection_order)
    if order_column is None:
        raise ValueError(f"Unsupported selection order: {selection_order}")

    conn = sqlite3.connect(store_path)
    try:
        # Force sort/window spill to disk and keep SQLite's page cache bounded.
        conn.execute("PRAGMA temp_store=FILE")
        conn.execute("PRAGMA cache_size=-2048")
        cursor = conn.execute(
            f"""
            SELECT payload
            FROM (
                SELECT
                    payload,
                    country,
                    category,
                    source_record_id,
                    sequence,
                    ROW_NUMBER() OVER (
                        PARTITION BY country, category
                        ORDER BY {order_column}
                    ) AS rn
                FROM nodes
            )
            ORDER BY rn, country, category, {order_column}
            LIMIT ?
            """,
            (max(0, int(target)),),
        )
        for (payload,) in cursor:
            yield json.loads(payload)
    finally:
        conn.close()


def write_streamed_partitions(
    store_path, target, partition_size, partition_dir, run_id, checkpoint_id,
    selection_order="sequence",
):
    """Stream selected nodes into one bounded partition buffer and incremental hashes."""
    parts = []
    country_distribution = {}
    category_distribution = {}
    source_distribution = {}
    website_domain_bearing_count = 0
    selected_count = 0
    selection_hash = hashlib.sha256()
    partition_nodes = []

    def flush_partition():
        if not partition_nodes:
            return
        partition_index = len(parts) + 1
        body = {
            "schema_version": "2.2",
            "run_id": run_id,
            "checkpoint_id": checkpoint_id,
            "partition_index": partition_index,
            "nodes": partition_nodes,
        }
        raw = json.dumps(body, separators=(",", ":"), sort_keys=True).encode("utf-8")
        part_path = os.path.join(partition_dir, f"partition-{partition_index:06d}.json")
        temp_path = part_path + ".tmp"
        with open(temp_path, "wb") as fh:
            fh.write(raw)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temp_path, part_path)
        part = {
            "partition_index": partition_index,
            "count": len(partition_nodes),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "path": part_path,
        }
        parts.append(part)
        print(
            "FORX_PROGRESS " + json.dumps(
                {
                    "run_id": run_id,
                    "stage": "PARTITION_WRITTEN",
                    "partition_index": partition_index,
                    "partition_count_so_far": len(parts),
                    "selected_count_so_far": selected_count,
                    "partition_sha256": part["sha256"],
                },
                separators=(",", ":"),
                sort_keys=True,
            ),
            flush=True,
        )
        partition_nodes.clear()

    for node in iter_diverse_nodes(store_path, target, selection_order):
        selected_count += 1
        source_record_id = str(node["source_record_id"])
        if selected_count > 1:
            selection_hash.update(b"\n")
        selection_hash.update(source_record_id.encode("utf-8"))
        country = node["country"]
        category = node["category"]
        source = node["source"]
        country_distribution[country] = country_distribution.get(country, 0) + 1
        category_distribution[category] = category_distribution.get(category, 0) + 1
        source_distribution[source] = source_distribution.get(source, 0) + 1
        if node.get("domain"):
            website_domain_bearing_count += 1
        partition_nodes.append(node)
        if len(partition_nodes) >= partition_size:
            flush_partition()

    flush_partition()
    return {
        "parts": parts,
        "selected_count": selected_count,
        "country_distribution": country_distribution,
        "category_distribution": category_distribution,
        "source_distribution": source_distribution,
        "website_domain_bearing_count": website_domain_bearing_count,
        "selection_sha256": selection_hash.hexdigest(),
    }

def load_audiala():
    """Stream the Audiala source to disk and deduplicate normalized nodes in SQLite."""
    fd, source_path = tempfile.mkstemp(prefix="amx-forx-audiala-", suffix=".csv")
    os.close(fd)
    store_path = create_node_store("amx-forx-audiala-")
    store_ready = False
    try:
        source_hash = hashlib.sha256()
        with requests.get(
            AUDIALA_URL,
            stream=True,
            timeout=180,
            headers={"User-Agent": "AMX-FORX-Audiala/2.0"},
        ) as response:
            response.raise_for_status()
            with open(source_path, "wb") as out:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        source_hash.update(chunk)
                        out.write(chunk)
        observed_sha = source_hash.hexdigest()
        if observed_sha != AUDIALA_FILE_SHA256:
            state["errors"].append(
                {
                    "type": "source_hash_mismatch",
                    "source": "audiala",
                    "expected": AUDIALA_FILE_SHA256,
                    "observed": observed_sha,
                }
            )

        raw_rows = 0
        rejected = 0
        duplicates = 0
        conn = sqlite3.connect(store_path)
        try:
            conn.execute("PRAGMA temp_store=FILE")
            conn.execute("PRAGMA cache_size=-4096")

            def pick(row, *cands):
                lookup = {norm(k): v for k, v in row.items()}
                for candidate in cands:
                    value = lookup.get(norm(candidate))
                    if value is not None and str(value).strip() != "":
                        return str(value).strip()
                return None

            def pick_prefix(row, prefixes):
                for key, value in row.items():
                    nk = norm(key)
                    if (
                        any(nk.startswith(norm(prefix)) for prefix in prefixes)
                        and value is not None
                        and str(value).strip() != ""
                    ):
                        return str(value).strip()
                return None

            with open(source_path, "r", encoding="utf-8-sig", newline="") as csv_file:
                for row in csv.DictReader(csv_file):
                    raw_rows += 1
                    qid = pick(row, "qid", "wikidata_qid", "wikidata", "wikidata_id", "id")
                    name = pick(row, "name_en", "english_name", "name", "label_en", "title_en") or pick_prefix(
                        row, ["name", "label", "title"]
                    )
                    lat = parse_float(pick(row, "latitude", "lat", "y"))
                    lon = parse_float(pick(row, "longitude", "lon", "lng", "long", "x"))
                    country = pick(row, "country_name", "country", "country_code", "country_iso2", "iso2", "countrycode")
                    category = pick(row, "type_slug", "place_type", "category_slug", "category", "type", "kind")
                    locality = pick(row, "city", "locality", "region", "admin1", "state", "province")
                    guide = pick(row, "url_en", "guide_url_en", "audiala_url_en", "url", "guide_url")

                    if not qid or not name or lat is None or lon is None or not country or not category:
                        rejected += 1
                        continue
                    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                        rejected += 1
                        continue

                    node = {
                        "source_record_id": f"wikidata:{qid}",
                        "name": name,
                        "latitude": lat,
                        "longitude": lon,
                        "country": country,
                        "locality": locality,
                        "category": category,
                        "website": None,
                        "domain": None,
                        "source_page": guide,
                        "source": "Audiala Places (Wikidata-backed POI dataset)",
                        "source_repo": AUDIALA_REPO,
                        "source_file": "data/audiala-places.csv",
                        "source_file_sha256": observed_sha,
                        "source_repo_commit": AUDIALA_REPO_COMMIT,
                        "license": AUDIALA_LICENSE,
                        "source_updated": AUDIALA_UPDATED,
                        "ingested_at": datetime.now(timezone.utc).isoformat(),
                        "confidence": "dataset-curated-coordinate",
                    }
                    cur = conn.execute(
                        "INSERT OR IGNORE INTO nodes "
                        "(ck,country,category,source_record_id,sequence,payload) "
                        "VALUES (?,?,?,?,?,?)",
                        (
                            canonical_key(name, lat, lon),
                            country,
                            category,
                            node["source_record_id"],
                            raw_rows,
                            json.dumps(node, separators=(",", ":"), sort_keys=True),
                        ),
                    )
                    if cur.rowcount == 0:
                        duplicates += 1
                    if raw_rows % 50000 == 0:
                        print(
                            "FORX_PROGRESS " + json.dumps(
                                {"run_id": RUN_ID, "stage": "AUDIALA_INGEST", "raw_rows": raw_rows,
                                 "rejected": rejected, "duplicates": duplicates},
                                separators=(",", ":"), sort_keys=True,
                            ),
                            flush=True,
                        )

            conn.commit()
        finally:
            conn.close()

        store_ready = True
        return {
            "node_store_path": store_path,
            "selection_order": "sequence",
            "raw_rows": raw_rows,
            "rejected": rejected,
            "duplicates": duplicates,
            "source_sha256": observed_sha,
            "source_url": AUDIALA_URL,
            "source_name": AUDIALA_REPO,
            "source_license": AUDIALA_LICENSE,
            "source_revision": AUDIALA_REPO_COMMIT,
        }
    finally:
        try:
            os.remove(source_path)
        except FileNotFoundError:
            pass
        if not store_ready:
            remove_sqlite(store_path)

def load_geonames():
    h = hashlib.sha256()
    fd, zip_path = tempfile.mkstemp(prefix="amx-forx-geonames-", suffix=".zip")
    os.close(fd)
    raw_rows = 0
    rejected = 0
    duplicates = 0
    latest_modified = None
    db_path = create_node_store("amx-forx-geonames-")
    store_ready = False

    try:
        with requests.get(
            GEONAMES_URL,
            stream=True,
            timeout=180,
            headers={"User-Agent": "AMX-FORX-GeoNames/2.1"},
        ) as r:
            r.raise_for_status()
            with open(zip_path, "wb") as out:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        h.update(chunk)
                        out.write(chunk)
        observed_sha = h.hexdigest()

        conn = sqlite3.connect(db_path)
        try:
            conn.execute("PRAGMA journal_mode=OFF")
            conn.execute("PRAGMA synchronous=OFF")
            conn.execute("PRAGMA temp_store=FILE")
            conn.execute("PRAGMA cache_size=-4096")

            with zipfile.ZipFile(zip_path) as zf:
                names = [n for n in zf.namelist() if n.endswith(".txt")]
                if not names:
                    raise RuntimeError("GeoNames archive contains no .txt payload")
                with zf.open(names[0], "r") as raw:
                    with io.TextIOWrapper(raw, encoding="utf-8", errors="replace", newline="") as payload:
                        for line in payload:
                            if not line.strip():
                                continue
                            raw_rows += 1
                            cols = line.rstrip("\n").split("\t")
                            if len(cols) < 19:
                                rejected += 1
                                continue

                            geonameid = cols[0].strip()
                            name = cols[1].strip() or cols[2].strip()
                            lat = parse_float(cols[4])
                            lon = parse_float(cols[5])
                            feature_class = cols[6].strip()
                            feature_code = cols[7].strip()
                            country = cols[8].strip()
                            admin1 = cols[10].strip()
                            population = cols[14].strip()
                            modified = cols[18].strip()

                            if not geonameid or not name or lat is None or lon is None or not country:
                                rejected += 1
                                continue
                            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                                rejected += 1
                                continue

                            ck = canonical_key(name, lat, lon)
                            category = f"{feature_class}:{feature_code}" if feature_code else feature_class or "place"
                            if modified and (latest_modified is None or modified > latest_modified):
                                latest_modified = modified

                            node = {
                                "source_record_id": f"geonames:{geonameid}",
                                "name": name,
                                "latitude": lat,
                                "longitude": lon,
                                "country": country,
                                "locality": admin1 or None,
                                "category": category,
                                "website": None,
                                "domain": None,
                                "source_page": f"https://www.geonames.org/{geonameid}/",
                                "source": GEONAMES_SOURCE,
                                "source_repo": "download.geonames.org/export/dump",
                                "source_file": "cities500.zip",
                                "source_file_sha256": observed_sha,
                                "source_repo_commit": None,
                                "license": GEONAMES_LICENSE,
                                "source_updated": modified or None,
                                "population": int(population) if population.isdigit() else None,
                                "ingested_at": datetime.now(timezone.utc).isoformat(),
                                "confidence": "geonames-curated-coordinate",
                            }
                            cur = conn.execute(
                                "INSERT OR IGNORE INTO nodes (ck,country,category,source_record_id,sequence,payload) VALUES (?,?,?,?,?,?)",
                                (ck, country, category, node["source_record_id"], raw_rows, json.dumps(node, separators=(",", ":"), sort_keys=True)),
                            )
                            if cur.rowcount == 0:
                                duplicates += 1
                            if raw_rows % 50000 == 0:
                                print(
                                    "FORX_PROGRESS " + json.dumps(
                                        {"run_id": RUN_ID, "stage": "GEONAMES_INGEST", "raw_rows": raw_rows,
                                         "rejected": rejected, "duplicates": duplicates},
                                        separators=(",", ":"), sort_keys=True,
                                    ),
                                    flush=True,
                                )

            conn.commit()
        finally:
            conn.close()

        store_ready = True
        return {
            "node_store_path": db_path,
            "selection_order": "source_record_id",
            "raw_rows": raw_rows,
            "rejected": rejected,
            "duplicates": duplicates,
            "source_sha256": observed_sha,
            "source_url": GEONAMES_URL,
            "source_name": GEONAMES_SOURCE,
            "source_license": GEONAMES_LICENSE,
            "source_revision": latest_modified,
        }
    finally:
        try:
            os.remove(zip_path)
        except FileNotFoundError:
            pass
        if not store_ready:
            remove_sqlite(db_path)

def combine_source_stores(a, g, target):
    """Preserve Audiala-then-GeoNames order and cross-source dedupe on disk."""
    combined_path = create_node_store("amx-forx-combined-")
    conn = sqlite3.connect(combined_path)
    cross_duplicates = 0
    sequence = 0
    try:
        conn.execute("PRAGMA temp_store=FILE")
        conn.execute("PRAGMA cache_size=-4096")
        for node in iter_store_nodes(a["node_store_path"]):
            sequence += 1
            cur = conn.execute(
                "INSERT OR IGNORE INTO nodes "
                "(ck,country,category,source_record_id,sequence,payload) VALUES (?,?,?,?,?,?)",
                (canonical_key(node["name"], node["latitude"], node["longitude"]),
                 node["country"], node["category"], node["source_record_id"], sequence,
                 json.dumps(node, separators=(",", ":"), sort_keys=True)),
            )
            if cur.rowcount == 0:
                cross_duplicates += 1

        # Preserve the former combined-mode contract: GeoNames contributed its
        # already-diverse top TARGET rows before the combined diversity pass.
        for node in iter_diverse_nodes(g["node_store_path"], target, "source_record_id"):
            sequence += 1
            cur = conn.execute(
                "INSERT OR IGNORE INTO nodes "
                "(ck,country,category,source_record_id,sequence,payload) VALUES (?,?,?,?,?,?)",
                (canonical_key(node["name"], node["latitude"], node["longitude"]),
                 node["country"], node["category"], node["source_record_id"], sequence,
                 json.dumps(node, separators=(",", ":"), sort_keys=True)),
            )
            if cur.rowcount == 0:
                cross_duplicates += 1
        conn.commit()
        return {
            "node_store_path": combined_path,
            "selection_order": "sequence",
            "raw_rows": a["raw_rows"] + g["raw_rows"],
            "rejected": a["rejected"] + g["rejected"],
            "duplicates": a["duplicates"] + g["duplicates"] + cross_duplicates,
            "source_sha256": hashlib.sha256(
                (a["source_sha256"] + g["source_sha256"]).encode()
            ).hexdigest(),
            "source_url": f"{AUDIALA_URL} + {GEONAMES_URL}",
            "source_name": "Audiala + GeoNames",
            "source_license": "CC BY 4.0",
            "source_revision": f"{AUDIALA_REPO_COMMIT}+{g['source_revision']}",
        }
    except Exception:
        remove_sqlite(combined_path)
        raise
    finally:
        conn.close()


def build():
    with lock:
        state["status"] = "RUNNING"
        state["phase"] = "SOURCE_INGESTION"
        state["started_at"] = datetime.now(timezone.utc).isoformat()
        state["errors"] = []

    source_store_paths = set()
    partition_dir = None
    try:
        if MODE == "stage1-proof" or SOURCE_ADAPTER == "audiala-stage1":
            source_result = load_audiala()
            source_store_paths.add(source_result["node_store_path"])
        elif SOURCE_ADAPTER == "geonames-cities500":
            source_result = load_geonames()
            source_store_paths.add(source_result["node_store_path"])
        elif SOURCE_ADAPTER == "audiala+geonames":
            a = load_audiala()
            source_store_paths.add(a["node_store_path"])
            g = load_geonames()
            source_store_paths.add(g["node_store_path"])
            source_result = combine_source_stores(a, g, TARGET)
            source_store_paths.add(source_result["node_store_path"])
            # The combined SQLite store now owns the deduplicated source sequence.
            # Remove both inputs before expensive selection to reduce disk pressure.
            for input_path in (a["node_store_path"], g["node_store_path"]):
                remove_sqlite(input_path)
                source_store_paths.discard(input_path)
        else:
            raise RuntimeError(f"Unsupported FORX_SOURCE_ADAPTER={SOURCE_ADAPTER}")

        print(
            "FORX_PROGRESS " + json.dumps(
                {
                    "run_id": RUN_ID,
                    "stage": "SOURCE_INGESTION_COMPLETE",
                    "source_adapter": SOURCE_ADAPTER,
                    "raw_rows": source_result["raw_rows"],
                    "rejected": source_result["rejected"],
                    "duplicates": source_result["duplicates"],
                },
                separators=(",", ":"), sort_keys=True,
            ),
            flush=True,
        )
        with lock:
            state["phase"] = "STREAMING_SELECTION_PARTITION_HASH"

        partition_dir = tempfile.mkdtemp(prefix=f"amx-forx-{RUN_ID}-")
        streamed = write_streamed_partitions(
            source_result["node_store_path"],
            TARGET,
            PARTITION_SIZE,
            partition_dir,
            RUN_ID,
            CHECKPOINT_ID,
            source_result["selection_order"],
        )
        parts = streamed["parts"]
        selected_count = streamed["selected_count"]
        cdist = streamed["country_distribution"]
        kdist = streamed["category_distribution"]
        source_dist = streamed["source_distribution"]
        domains = streamed["website_domain_bearing_count"]
        selection_sha256 = streamed["selection_sha256"]
        completed = datetime.now(timezone.utc).isoformat()
        threshold = 1000 if MODE == "stage1-proof" else TARGET

        manifest = {
            "schema_version": "2.2",
            "manifest_type": "FORX_PRODUCTION_MANIFEST" if MODE != "stage1-proof" else "FORX_STAGE1_MANIFEST",
            "mode": MODE,
            "run_id": RUN_ID,
            "checkpoint_id": CHECKPOINT_ID,
            "source_adapter": SOURCE_ADAPTER,
            "source": source_result["source_name"],
            "source_url": source_result["source_url"],
            "source_license": source_result["source_license"],
            "source_revision": source_result["source_revision"],
            "source_file_sha256": source_result["source_sha256"],
            "target": TARGET,
            "partition_size": PARTITION_SIZE,
            "partition_count": len(parts),
            "partition_hashes": {str(p["partition_index"]): p["sha256"] for p in parts},
            "selected_count": selected_count,
            "selection_sha256": selection_sha256,
            "source_cursor_start": 0,
            "source_cursor_next": selected_count,
            "cumulative_unique_count_snapshot": selected_count,
            "raw_rows_ingested": source_result["raw_rows"],
            "rows_rejected": source_result["rejected"],
            "duplicates_removed": source_result["duplicates"],
            "country_count": len(cdist),
            "category_count": len(kdist),
            "source_distribution": source_dist,
            "website_domain_bearing_count": domains,
            "started_at": state["started_at"],
            "completed_at": completed,
        }

        receipt = {
            "schema_version": "2.2",
            "receipt_type": "FORX_STAGE1_RUNTIME_OUTPUT" if MODE == "stage1-proof" else "FORX_PRODUCTION_RUNTIME_OUTPUT",
            "status": (
                "RUNTIME_COMPLETE_NOT_YET_DURABLY_VERIFIED"
                if MODE == "stage1-proof" and selected_count >= threshold
                else "PRODUCTION_RUNTIME_COMPLETE_NOT_YET_DURABLY_VERIFIED"
                if MODE != "stage1-proof" and selected_count >= threshold
                else "RUNTIME_UNDER_THRESHOLD"
            ),
            "mode": MODE,
            "run_id": RUN_ID,
            "checkpoint_id": CHECKPOINT_ID,
            "source_adapter": SOURCE_ADAPTER,
            "source": source_result["source_name"],
            "source_url": source_result["source_url"],
            "source_license": source_result["source_license"],
            "source_revision": source_result["source_revision"],
            "source_file_sha256_observed": source_result["source_sha256"],
            "raw_rows_ingested": source_result["raw_rows"],
            "rows_rejected": source_result["rejected"],
            "duplicates_removed": source_result["duplicates"],
            "normalized_selected_nodes": selected_count,
            "coordinate_backed_count": selected_count,
            "country_count": len(cdist),
            "country_distribution": cdist,
            "category_count": len(kdist),
            "category_distribution": kdist,
            "source_distribution": source_dist,
            "website_domain_bearing_count": domains,
            "target": TARGET,
            "partition_count": len(parts),
            "partition_size": PARTITION_SIZE,
            "partition_hashes": {str(p["partition_index"]): p["sha256"] for p in parts},
            "selection_sha256": selection_sha256,
            "source_cursor_start": 0,
            "source_cursor_next": selected_count,
            "cumulative_unique_count_snapshot": selected_count,
            "started_at": state["started_at"],
            "completed_at": completed,
            "errors": state["errors"],
            "uncertainty_notes": [
                "Bulk runtime does not perform deep identity resolution.",
                "Runtime output alone is not production PASS; durable persistence and independent readback remain required.",
                "Historical Stage-1 PASS remains immutable provenance and must not receive duplicate productive credit.",
                "GeoNames cities500 represents global populated places, not a business-ownership registry; downstream iSCOPE must not treat every node as a prospect without qualification.",
                "Source ingestion, diversity selection, partition serialization and selection hashing are streamed with disk-backed SQLite and a single bounded partition buffer.",
                "Partition artifacts remain instance-local until the existing authorized durable-output route independently persists and reads them back.",
            ],
        }

        with lock:
            state.update(
                {
                    "node_count": selected_count,
                    "partitions": parts,
                    "partition_dir": partition_dir,
                    "manifest": manifest,
                    "receipt": receipt,
                    "completed_at": completed,
                    "phase": "RUNTIME_OUTPUT_READY_NOT_DURABLY_VERIFIED",
                    "status": "COMPLETE" if selected_count >= threshold else "UNDER_THRESHOLD",
                }
            )

        print("FORX_PRODUCTION_MANIFEST " + json.dumps(manifest, separators=(",", ":"), sort_keys=True), flush=True)
        print("FORX_RUNTIME_RECEIPT " + json.dumps(receipt, separators=(",", ":"), sort_keys=True), flush=True)

    except Exception as e:
        with lock:
            state["errors"].append({"type": "runtime_exception", "error": repr(e)})
            state["phase"] = "FAILED"
            state["status"] = "FAILED"
        print("FORX_RUNTIME_FAILURE " + repr(e), flush=True)
    finally:
        for store_path in tuple(source_store_paths):
            remove_sqlite(store_path)
        if partition_dir and state.get("status") == "FAILED":
            shutil.rmtree(partition_dir, ignore_errors=True)


@app.on_event("startup")
def startup():
    threading.Thread(target=build, daemon=True).start()


@app.get("/")
def root():
    return {
        "service": "AMX FORX Bulk Runtime",
        "mode": MODE,
        "run_id": RUN_ID,
        "status": state["status"],
        "target": TARGET,
        "partition_size": PARTITION_SIZE,
        "source_adapter": SOURCE_ADAPTER,
    }


@app.get("/status")
def status():
    r = state.get("receipt") or {}
    return {
        "status": state["status"],
        "phase": state.get("phase"),
        "mode": MODE,
        "run_id": RUN_ID,
        "node_count": state.get("node_count", 0),
        "partition_count": len(state.get("partitions") or []),
        "partition_size": PARTITION_SIZE,
        "target": TARGET,
        "source_adapter": SOURCE_ADAPTER,
        "country_count": r.get("country_count"),
        "category_count": r.get("category_count"),
        "errors": state.get("errors"),
    }


@app.get("/partition/{idx}")
def partition(idx: int):
    parts = state.get("partitions") or []
    if idx < 1 or idx > len(parts):
        raise HTTPException(404)
    part = parts[idx - 1]
    # Return the exact stored bytes that were hashed when the partition was written.
    # Re-serializing the parsed JSON can change the byte stream (for example Unicode
    # escaping) and makes the durable readback SHA gate fail despite equivalent JSON.
    with open(part["path"], "rb") as fh:
        raw = fh.read()
    return Response(content=raw, media_type="application/json")


@app.get("/manifest")
def manifest():
    if not state.get("manifest"):
        raise HTTPException(425, "not complete")
    return JSONResponse(state["manifest"])


@app.get("/runtime-receipt")
def runtime_receipt():
    if not state.get("receipt"):
        raise HTTPException(425, "not complete")
    return JSONResponse(state["receipt"])
