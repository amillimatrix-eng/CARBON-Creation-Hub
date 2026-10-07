import csv, hashlib, io, json, os, threading
from datetime import datetime, timezone
from urllib.parse import urlparse
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI(title="AMX FORX Stage-1 Proof Runtime")

SOURCE_URL = "https://huggingface.co/datasets/audiala/audiala-places/resolve/main/data/audiala-places.csv"
SOURCE_REPO = "audiala/audiala-places"
SOURCE_LICENSE = "CC BY 4.0"
SOURCE_FILE_SHA256 = "e21c7e92357ea062db51445baaaef1fa45fedb24cf095b72b520199f86b2b47c"
SOURCE_REPO_COMMIT = "e033fb7"
SOURCE_UPDATED = "2026-09-28"
TARGET = 1200
PARTITION_SIZE = 100

state={"status":"STARTING","started_at":None,"completed_at":None,"nodes":[],"partitions":[],"receipt":None,"errors":[]}
lock=threading.Lock()

def norm(s):
    return "".join(ch.lower() for ch in str(s or "") if ch.isalnum())

def pick(row, *cands):
    lookup={norm(k):v for k,v in row.items()}
    for c in cands:
        v=lookup.get(norm(c))
        if v is not None and str(v).strip()!="":
            return str(v).strip()
    return None

def pick_prefix(row, prefixes):
    for k,v in row.items():
        nk=norm(k)
        if any(nk.startswith(norm(p)) for p in prefixes) and v is not None and str(v).strip()!="":
            return str(v).strip()
    return None

def domain_of(url):
    if not url: return None
    try:
        u=url if "://" in url else "https://"+url
        h=(urlparse(u).hostname or "").lower()
        return h[4:] if h.startswith("www.") else h or None
    except Exception:
        return None

def parse_float(v):
    try: return float(v)
    except Exception: return None

def build():
    with lock:
        state["status"]="RUNNING"
        state["started_at"]=datetime.now(timezone.utc).isoformat()
    tmp="/tmp/audiala-places.csv"
    raw_rows=0; rejected=0; duplicates=0
    try:
        with requests.get(SOURCE_URL, stream=True, timeout=120, headers={"User-Agent":"AMX-FORX-Stage1/1.0"}) as r:
            r.raise_for_status()
            h=hashlib.sha256()
            with open(tmp,"wb") as fh:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk:
                        h.update(chunk); fh.write(chunk)
        observed_source_sha=h.hexdigest()
        if observed_source_sha != SOURCE_FILE_SHA256:
            state["errors"].append({"type":"source_hash_mismatch","expected":SOURCE_FILE_SHA256,"observed":observed_source_sha})
        dedup={}
        with open(tmp,"r",encoding="utf-8-sig",newline="") as fh:
            reader=csv.DictReader(fh)
            headers=reader.fieldnames or []
            print("FORX_SOURCE_HEADERS "+json.dumps(headers,separators=(",",":")),flush=True)
            for row in reader:
                raw_rows += 1
                qid=pick(row,"qid","wikidata_qid","wikidata","wikidata_id","id")
                name=pick(row,"name_en","english_name","name","label_en","title_en") or pick_prefix(row,["name","label","title"])
                lat=parse_float(pick(row,"latitude","lat","y"))
                lon=parse_float(pick(row,"longitude","lon","lng","long","x"))
                country=pick(row,"country_name","country","country_code","country_iso2","iso2","countrycode")
                category=pick(row,"type_slug","place_type","category_slug","category","type","kind")
                locality=pick(row,"city","locality","region","admin1","state","province")
                guide=pick(row,"url_en","guide_url_en","audiala_url_en","url","guide_url")
                if not qid or not name or lat is None or lon is None or not country or not category:
                    rejected += 1; continue
                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    rejected += 1; continue
                key=f"wikidata:{qid}"
                if key in dedup:
                    duplicates += 1; continue
                dedup[key]={
                    "source_record_id":key,
                    "name":name,
                    "latitude":lat,
                    "longitude":lon,
                    "country":country,
                    "locality":locality,
                    "category":category,
                    "website":None,
                    "domain":None,
                    "source_page":guide,
                    "source":"Audiala Places (Wikidata-backed POI dataset)",
                    "source_repo":SOURCE_REPO,
                    "source_file":"data/audiala-places.csv",
                    "source_file_sha256":observed_source_sha,
                    "source_repo_commit":SOURCE_REPO_COMMIT,
                    "license":SOURCE_LICENSE,
                    "source_updated":SOURCE_UPDATED,
                    "ingested_at":datetime.now(timezone.utc).isoformat(),
                    "confidence":"dataset-curated-coordinate"
                }
        nodes=list(dedup.values())

        # diversity-preserving round robin across countries, then categories
        by_country={}
        for n in nodes:
            by_country.setdefault(n["country"],{}).setdefault(n["category"],[]).append(n)
        chosen=[]
        positions={(c,k):0 for c,ks in by_country.items() for k in ks}
        countries=sorted(by_country)
        while len(chosen)<min(TARGET,len(nodes)):
            progressed=False
            for c in countries:
                for k in sorted(by_country[c]):
                    pos=positions[(c,k)]
                    arr=by_country[c][k]
                    if pos < len(arr):
                        chosen.append(arr[pos]); positions[(c,k)]=pos+1; progressed=True
                        if len(chosen)>=TARGET: break
                if len(chosen)>=TARGET: break
            if not progressed: break
        nodes=chosen
        parts=[]
        for i in range(0,len(nodes),PARTITION_SIZE):
            body={"schema_version":"1.0","partition_index":len(parts)+1,"nodes":nodes[i:i+PARTITION_SIZE]}
            raw=json.dumps(body,separators=(",",":"),sort_keys=True)
            parts.append({"partition_index":len(parts)+1,"count":len(body["nodes"]),"sha256":hashlib.sha256(raw.encode()).hexdigest(),"body":body})
        cdist={}; kdist={}; domains=0
        for n in nodes:
            cdist[n["country"]]=cdist.get(n["country"],0)+1
            kdist[n["category"]]=kdist.get(n["category"],0)+1
            if n.get("domain"): domains += 1
        completed=datetime.now(timezone.utc).isoformat()
        receipt={
            "schema_version":"1.0",
            "receipt_type":"FORX_STAGE1_RUNTIME_OUTPUT",
            "status":"RUNTIME_COMPLETE_NOT_YET_DURABLY_VERIFIED" if len(nodes)>=1000 else "RUNTIME_UNDER_THRESHOLD",
            "source":SOURCE_REPO,
            "source_url":SOURCE_URL,
            "source_license":SOURCE_LICENSE,
            "source_repo_commit":SOURCE_REPO_COMMIT,
            "source_file_sha256_expected":SOURCE_FILE_SHA256,
            "source_file_sha256_observed":observed_source_sha,
            "raw_rows_ingested":raw_rows,
            "rows_rejected":rejected,
            "duplicates_removed":duplicates,
            "normalized_selected_nodes":len(nodes),
            "coordinate_backed_count":len(nodes),
            "country_count":len(cdist),
            "country_distribution":cdist,
            "category_count":len(kdist),
            "category_distribution":kdist,
            "website_domain_bearing_count":domains,
            "partition_count":len(parts),
            "partition_size":PARTITION_SIZE,
            "partition_hashes":{str(p["partition_index"]):p["sha256"] for p in parts},
            "started_at":state["started_at"],
            "completed_at":completed,
            "errors":state["errors"],
            "uncertainty_notes":[
                "Stage 1 does not perform deep identity resolution.",
                "source_page is provenance/guide metadata and is not represented as a business-owned website.",
                "Runtime output alone is not Stage-1 PASS; durable persistence and independent readback remain required."
            ]
        }
        with lock:
            state.update({"nodes":nodes,"partitions":parts,"receipt":receipt,"completed_at":completed,"status":"COMPLETE" if len(nodes)>=1000 else "UNDER_THRESHOLD"})
        for p in parts:
            print(f"FORX_PART_{p['partition_index']:03d} "+json.dumps(p["body"],separators=(",",":"),sort_keys=True),flush=True)
        print("FORX_RUNTIME_RECEIPT "+json.dumps(receipt,separators=(",",":"),sort_keys=True),flush=True)
    except Exception as e:
        with lock:
            state["errors"].append({"type":"runtime_exception","error":repr(e)})
            state["status"]="FAILED"
        print("FORX_RUNTIME_FAILURE "+repr(e),flush=True)

@app.on_event("startup")
def startup():
    threading.Thread(target=build,daemon=True).start()

@app.get("/")
def root():
    return {"service":"AMX FORX Stage-1 Proof Runtime","status":state["status"]}

@app.get("/status")
def status():
    r=state.get("receipt") or {}
    return {"status":state["status"],"node_count":len(state.get("nodes") or []),"partition_count":len(state.get("partitions") or []),"country_count":r.get("country_count"),"category_count":r.get("category_count"),"errors":state.get("errors")}

@app.get("/partition/{idx}")
def partition(idx:int):
    parts=state.get("partitions") or []
    if idx<1 or idx>len(parts): raise HTTPException(404)
    return JSONResponse(parts[idx-1]["body"])

@app.get("/runtime-receipt")
def runtime_receipt():
    if not state.get("receipt"): raise HTTPException(425,"not complete")
    return JSONResponse(state["receipt"])
