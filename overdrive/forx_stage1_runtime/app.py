import json, threading, time, hashlib
from datetime import datetime, timezone
from urllib.parse import urlparse
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI(title="AMX FORX Stage-1 Proof Runtime")

OVERPASS_ENDPOINTS = ["https://overpass-api.de/api/interpreter","https://overpass.kumi.systems/api/interpreter"]
TARGET = 1200
PARTITION_SIZE = 100
PER_REGION = 180

REGIONS = [
    {"country":"South Africa","country_code":"ZA","locality":"Cape Town","bbox":"-34.05,18.30,-33.80,18.65"},
    {"country":"United Kingdom","country_code":"GB","locality":"London","bbox":"51.40,-0.25,51.62,0.10"},
    {"country":"Germany","country_code":"DE","locality":"Berlin","bbox":"52.40,13.20,52.60,13.55"},
    {"country":"France","country_code":"FR","locality":"Paris","bbox":"48.80,2.20,48.92,2.45"},
    {"country":"United States","country_code":"US","locality":"New York","bbox":"40.65,-74.10,40.85,-73.85"},
    {"country":"Canada","country_code":"CA","locality":"Toronto","bbox":"43.60,-79.55,43.80,-79.20"},
    {"country":"Australia","country_code":"AU","locality":"Sydney","bbox":"-33.98,151.05,-33.75,151.30"},
    {"country":"Japan","country_code":"JP","locality":"Tokyo","bbox":"35.60,139.60,35.78,139.85"}
]
CATEGORY_KEYS = ["amenity","shop","tourism","office","craft","healthcare","leisure"]

state = {
    "status":"STARTING",
    "started_at":None,
    "completed_at":None,
    "nodes":[],
    "partitions":[],
    "receipt":None,
    "errors":[]
}
lock = threading.Lock()

def domain_of(url):
    if not url:
        return None
    try:
        u = url if "://" in url else "https://" + url
        host = (urlparse(u).hostname or "").lower()
        return host[4:] if host.startswith("www.") else host or None
    except Exception:
        return None

def classify(tags):
    for k in CATEGORY_KEYS:
        if tags.get(k):
            return f"{k}:{tags.get(k)}"
    return "other:unknown"

def coord(el):
    if el.get("type") == "node":
        return el.get("lat"), el.get("lon")
    c = el.get("center") or {}
    return c.get("lat"), c.get("lon")

def query_region(r):
    bbox = r["bbox"]
    q = f"""[out:json][timeout:40];
(
  nwr["name"]["amenity"]({bbox});
  nwr["name"]["shop"]({bbox});
  nwr["name"]["tourism"]({bbox});
  nwr["name"]["office"]({bbox});
  nwr["name"]["craft"]({bbox});
  nwr["name"]["healthcare"]({bbox});
  nwr["name"]["leisure"]({bbox});
);
out center tags 500;"""
    resp = requests.post(OVERPASS, data={"data":q}, timeout=70, headers={"User-Agent":"AMX-FORX-Stage1/1.0"})
    resp.raise_for_status()
    payload = resp.json()
    fetched = payload.get("elements", [])
    buckets = {}
    for el in fetched:
        tags = el.get("tags") or {}
        name = (tags.get("name") or "").strip()
        lat, lon = coord(el)
        if not name or lat is None or lon is None:
            continue
        try:
            lat = float(lat); lon = float(lon)
        except Exception:
            continue
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            continue
        cat = classify(tags)
        website = tags.get("website") or tags.get("contact:website")
        node = {
            "source_record_id": f"osm:{el.get('type')}:{el.get('id')}",
            "name": name,
            "latitude": lat,
            "longitude": lon,
            "country": r["country"],
            "country_code": r["country_code"],
            "locality": r["locality"],
            "region": None,
            "category": cat,
            "website": website,
            "domain": domain_of(website),
            "source": "OpenStreetMap via Overpass API",
            "source_url": "https://www.openstreetmap.org/",
            "license": "Open Database License (ODbL) 1.0",
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "confidence": "source-tagged-coordinate",
            "osm_tags": {k:v for k,v in tags.items() if k in ["amenity","shop","tourism","office","craft","healthcare","leisure","website","contact:website"]}
        }
        buckets.setdefault(cat, []).append(node)
    # round robin across categories to avoid category monoculture
    cats = sorted(buckets)
    out = []
    idx = {c:0 for c in cats}
    while len(out) < PER_REGION:
        progressed = False
        for c in cats:
            i = idx[c]
            if i < len(buckets[c]):
                out.append(buckets[c][i]); idx[c] += 1; progressed = True
                if len(out) >= PER_REGION: break
        if not progressed: break
    return out, len(fetched)

def build():
    with lock:
        state["status"] = "RUNNING"
        state["started_at"] = datetime.now(timezone.utc).isoformat()
    all_nodes = []
    raw_rows = 0
    for r in REGIONS:
        try:
            nodes, raw = query_region(r)
            raw_rows += raw
            all_nodes.extend(nodes)
        except Exception as e:
            with lock:
                state["errors"].append({"region":r["locality"],"error":repr(e)})
    # exact source-id dedupe
    dedup = {}
    dupes = 0
    for n in all_nodes:
        k = n["source_record_id"]
        if k in dedup:
            dupes += 1
        else:
            dedup[k] = n
    nodes = list(dedup.values())
    # deterministic country round robin until target
    by_country = {}
    for n in nodes:
        by_country.setdefault(n["country_code"], []).append(n)
    ordered = []
    pos = {k:0 for k in by_country}
    while len(ordered) < min(TARGET, len(nodes)):
        progressed = False
        for k in sorted(by_country):
            i=pos[k]
            if i < len(by_country[k]):
                ordered.append(by_country[k][i]); pos[k]+=1; progressed=True
                if len(ordered) >= TARGET: break
        if not progressed: break
    nodes = ordered
    partitions = []
    for i in range(0,len(nodes),PARTITION_SIZE):
        pnodes = nodes[i:i+PARTITION_SIZE]
        body = {"schema_version":"1.0","partition_index":len(partitions)+1,"nodes":pnodes}
        raw = json.dumps(body, separators=(",",":"), sort_keys=True)
        partitions.append({
            "partition_index":len(partitions)+1,
            "count":len(pnodes),
            "sha256":hashlib.sha256(raw.encode()).hexdigest(),
            "body":body
        })
    countries={}
    categories={}
    domains=0
    for n in nodes:
        countries[n["country"]] = countries.get(n["country"],0)+1
        categories[n["category"]] = categories.get(n["category"],0)+1
        if n.get("domain"): domains += 1
    completed = datetime.now(timezone.utc).isoformat()
    receipt = {
        "schema_version":"1.0",
        "receipt_type":"FORX_STAGE1_RUNTIME_OUTPUT",
        "status":"RUNTIME_COMPLETE_NOT_YET_DURABLY_VERIFIED",
        "source":"OpenStreetMap via Overpass API",
        "source_terms":"ODbL 1.0",
        "raw_rows_fetched":raw_rows,
        "normalized_unique_nodes":len(nodes),
        "duplicates_removed":dupes,
        "rejected_or_not_selected":max(0,raw_rows-len(nodes)-dupes),
        "coordinate_backed_count":len(nodes),
        "country_count":len(countries),
        "country_distribution":countries,
        "category_count":len(categories),
        "category_distribution":categories,
        "website_domain_bearing_count":domains,
        "partition_count":len(partitions),
        "partition_size":PARTITION_SIZE,
        "started_at":state["started_at"],
        "completed_at":completed,
        "errors":state["errors"],
        "truth_boundary":"Runtime output only. Stage-1 PASS requires durable persistence plus independent readback."
    }
    with lock:
        state["nodes"] = nodes
        state["partitions"] = partitions
        state["receipt"] = receipt
        state["completed_at"] = completed
        state["status"] = "COMPLETE" if len(nodes) >= 1000 else "UNDER_THRESHOLD"

@app.on_event("startup")
def startup():
    threading.Thread(target=build, daemon=True).start()

@app.get("/")
def root():
    return {"service":"AMX FORX Stage-1 Proof Runtime","status":state["status"]}

@app.get("/status")
def status():
    r=state.get("receipt")
    return {
        "status":state["status"],
        "node_count": len(state.get("nodes") or []),
        "partition_count": len(state.get("partitions") or []),
        "country_count": (r or {}).get("country_count"),
        "category_count": (r or {}).get("category_count"),
        "errors": state.get("errors")
    }

@app.get("/partition/{idx}")
def partition(idx:int):
    parts=state.get("partitions") or []
    if idx < 1 or idx > len(parts):
        raise HTTPException(404)
    return JSONResponse(parts[idx-1]["body"])

@app.get("/runtime-receipt")
def runtime_receipt():
    if not state.get("receipt"):
        raise HTTPException(425, "not complete")
    return JSONResponse(state["receipt"])
