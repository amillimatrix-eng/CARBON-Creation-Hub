import csv, hashlib, io, json, os, sqlite3, tempfile, threading, zipfile
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

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


def fetch_bytes(url, user_agent):
    h = hashlib.sha256()
    buf = io.BytesIO()
    with requests.get(url, stream=True, timeout=180, headers={"User-Agent": user_agent}) as r:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                h.update(chunk)
                buf.write(chunk)
    return buf.getvalue(), h.hexdigest()


def load_audiala():
    raw, observed_sha = fetch_bytes(AUDIALA_URL, "AMX-FORX-Audiala/2.0")
    if observed_sha != AUDIALA_FILE_SHA256:
        state["errors"].append(
            {
                "type": "source_hash_mismatch",
                "source": "audiala",
                "expected": AUDIALA_FILE_SHA256,
                "observed": observed_sha,
            }
        )

    text_data = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text_data))
    raw_rows = 0
    rejected = 0
    duplicates = 0
    dedup = {}

    def pick(row, *cands):
        lookup = {norm(k): v for k, v in row.items()}
        for c in cands:
            v = lookup.get(norm(c))
            if v is not None and str(v).strip() != "":
                return str(v).strip()
        return None

    def pick_prefix(row, prefixes):
        for k, v in row.items():
            nk = norm(k)
            if any(nk.startswith(norm(p)) for p in prefixes) and v is not None and str(v).strip() != "":
                return str(v).strip()
        return None

    for row in reader:
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

        ck = canonical_key(name, lat, lon)
        if ck in dedup:
            duplicates += 1
            continue

        dedup[ck] = {
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

    return {
        "nodes": list(dedup.values()),
        "raw_rows": raw_rows,
        "rejected": rejected,
        "duplicates": duplicates,
        "source_sha256": observed_sha,
        "source_url": AUDIALA_URL,
        "source_name": AUDIALA_REPO,
        "source_license": AUDIALA_LICENSE,
        "source_revision": AUDIALA_REPO_COMMIT,
    }


def load_geonames():
    h = hashlib.sha256()
    fd, zip_path = tempfile.mkstemp(prefix="amx-forx-geonames-", suffix=".zip")
    os.close(fd)
    raw_rows = 0
    rejected = 0
    duplicates = 0
    latest_modified = None
    db_fd, db_path = tempfile.mkstemp(prefix="amx-forx-geonames-", suffix=".sqlite3")
    os.close(db_fd)

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
            conn.execute(
                """
                CREATE TABLE nodes (
                    ck TEXT PRIMARY KEY,
                    country TEXT NOT NULL,
                    category TEXT NOT NULL,
                    source_record_id TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )

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
                                "INSERT OR IGNORE INTO nodes (ck,country,category,source_record_id,payload) VALUES (?,?,?,?,?)",
                                (ck, country, category, node["source_record_id"], json.dumps(node, separators=(",", ":"), sort_keys=True)),
                            )
                            if cur.rowcount == 0:
                                duplicates += 1

            conn.commit()
            rows = conn.execute(
                """
                SELECT payload
                FROM (
                    SELECT
                        payload,
                        country,
                        category,
                        source_record_id,
                        ROW_NUMBER() OVER (
                            PARTITION BY country, category
                            ORDER BY source_record_id
                        ) AS rn
                    FROM nodes
                )
                ORDER BY rn, country, category, source_record_id
                LIMIT ?
                """,
                (TARGET,),
            )
            selected = [json.loads(row[0]) for row in rows]
        finally:
            conn.close()

        return {
            "nodes": selected,
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
        for path in (zip_path, db_path):
            try:
                os.remove(path)
            except FileNotFoundError:
                pass

def choose_diverse(nodes, target):
    by_country = {}
    for n in nodes:
        by_country.setdefault(n["country"], {}).setdefault(n["category"], []).append(n)

    chosen = []
    positions = {(c, k): 0 for c, ks in by_country.items() for k in ks}
    countries = sorted(by_country)

    while len(chosen) < min(target, len(nodes)):
        progressed = False
        for c in countries:
            for k in sorted(by_country[c]):
                pos = positions[(c, k)]
                arr = by_country[c][k]
                if pos < len(arr):
                    chosen.append(arr[pos])
                    positions[(c, k)] = pos + 1
                    progressed = True
                    if len(chosen) >= target:
                        break
            if len(chosen) >= target:
                break
        if not progressed:
            break
    return chosen


def build():
    with lock:
        state["status"] = "RUNNING"
        state["started_at"] = datetime.now(timezone.utc).isoformat()
        state["errors"] = []

    try:
        if MODE == "stage1-proof" or SOURCE_ADAPTER == "audiala-stage1":
            source_result = load_audiala()
        elif SOURCE_ADAPTER == "geonames-cities500":
            source_result = load_geonames()
        elif SOURCE_ADAPTER == "audiala+geonames":
            a = load_audiala()
            g = load_geonames()
            combined = {}
            duplicates = a["duplicates"] + g["duplicates"]
            for node in a["nodes"] + g["nodes"]:
                ck = canonical_key(node["name"], node["latitude"], node["longitude"])
                if ck in combined:
                    duplicates += 1
                    continue
                combined[ck] = node
            source_result = {
                "nodes": list(combined.values()),
                "raw_rows": a["raw_rows"] + g["raw_rows"],
                "rejected": a["rejected"] + g["rejected"],
                "duplicates": duplicates,
                "source_sha256": hashlib.sha256(
                    (a["source_sha256"] + g["source_sha256"]).encode()
                ).hexdigest(),
                "source_url": f"{AUDIALA_URL} + {GEONAMES_URL}",
                "source_name": "Audiala + GeoNames",
                "source_license": "CC BY 4.0",
                "source_revision": f"{AUDIALA_REPO_COMMIT}+{g['source_revision']}",
            }
        else:
            raise RuntimeError(f"Unsupported FORX_SOURCE_ADAPTER={SOURCE_ADAPTER}")

        nodes = choose_diverse(source_result["nodes"], TARGET)

        parts = []
        partition_dir = tempfile.mkdtemp(prefix=f"amx-forx-{RUN_ID}-")
        for i in range(0, len(nodes), PARTITION_SIZE):
            body = {
                "schema_version": "2.2",
                "run_id": RUN_ID,
                "checkpoint_id": CHECKPOINT_ID,
                "partition_index": len(parts) + 1,
                "nodes": nodes[i : i + PARTITION_SIZE],
            }
            raw = json.dumps(body, separators=(",", ":"), sort_keys=True)
            part_index = len(parts) + 1
            part_path = os.path.join(partition_dir, f"partition-{part_index:06d}.json")
            with open(part_path, "w", encoding="utf-8") as fh:
                fh.write(raw)
            parts.append(
                {
                    "partition_index": part_index,
                    "count": len(body["nodes"]),
                    "sha256": hashlib.sha256(raw.encode()).hexdigest(),
                    "path": part_path,
                }
            )
        cdist = {}
        kdist = {}
        source_dist = {}
        domains = 0
        for n in nodes:
            cdist[n["country"]] = cdist.get(n["country"], 0) + 1
            kdist[n["category"]] = kdist.get(n["category"], 0) + 1
            source_dist[n["source"]] = source_dist.get(n["source"], 0) + 1
            if n.get("domain"):
                domains += 1

        id_raw = "\n".join(n["source_record_id"] for n in nodes)
        selection_sha256 = hashlib.sha256(id_raw.encode()).hexdigest()
        completed = datetime.now(timezone.utc).isoformat()

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
            "selected_count": len(nodes),
            "selection_sha256": selection_sha256,
            "source_cursor_start": 0,
            "source_cursor_next": len(nodes),
            "cumulative_unique_count_snapshot": len(nodes),
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

        threshold = 1000 if MODE == "stage1-proof" else TARGET
        receipt = {
            "schema_version": "2.2",
            "receipt_type": "FORX_STAGE1_RUNTIME_OUTPUT" if MODE == "stage1-proof" else "FORX_PRODUCTION_RUNTIME_OUTPUT",
            "status": (
                "RUNTIME_COMPLETE_NOT_YET_DURABLY_VERIFIED"
                if MODE == "stage1-proof" and len(nodes) >= threshold
                else "PRODUCTION_RUNTIME_COMPLETE_NOT_YET_DURABLY_VERIFIED"
                if MODE != "stage1-proof" and len(nodes) >= threshold
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
            "normalized_selected_nodes": len(nodes),
            "coordinate_backed_count": len(nodes),
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
            "source_cursor_next": len(nodes),
            "cumulative_unique_count_snapshot": len(nodes),
            "started_at": state["started_at"],
            "completed_at": completed,
            "errors": state["errors"],
            "uncertainty_notes": [
                "Bulk runtime does not perform deep identity resolution.",
                "Runtime output alone is not production PASS; durable persistence and independent readback remain required.",
                "Historical Stage-1 PASS remains immutable provenance and must not receive duplicate productive credit.",
                "GeoNames cities500 represents global populated places, not a business-ownership registry; downstream iSCOPE must not treat every node as a prospect without qualification.",
                "Production source ingestion is disk-backed and streamed; partition bodies are file-backed in the running instance to avoid retaining the full source and all partition payloads in RAM.",
                "Instance-local partition files are not durable acceptance evidence by themselves; external persistence plus independent readback remains required.",
            ],
        }

        with lock:
            state.update(
                {
                    "node_count": len(nodes),
                    "partitions": parts,
                    "partition_dir": partition_dir,
                    "manifest": manifest,
                    "receipt": receipt,
                    "completed_at": completed,
                    "status": "COMPLETE" if len(nodes) >= threshold else "UNDER_THRESHOLD",
                }
            )

        print("FORX_PRODUCTION_MANIFEST " + json.dumps(manifest, separators=(",", ":"), sort_keys=True), flush=True)
        print("FORX_RUNTIME_RECEIPT " + json.dumps(receipt, separators=(",", ":"), sort_keys=True), flush=True)

    except Exception as e:
        with lock:
            state["errors"].append({"type": "runtime_exception", "error": repr(e)})
            state["status"] = "FAILED"
        print("FORX_RUNTIME_FAILURE " + repr(e), flush=True)


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
    with open(part["path"], "r", encoding="utf-8") as fh:
        return JSONResponse(json.load(fh))


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
