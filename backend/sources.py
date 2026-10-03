"""Append-only Drive inventory enrollment under an explicitly scoped read remote."""
from __future__ import annotations
import hashlib
import json
import re
import subprocess


def drive_inventory(registry: dict, records: list[dict], remote: str, prior_sources: list[dict] = ()) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9_-]+:[^\r\n\0]*", remote):
        raise ValueError("INVALID_SCOPED_DRIVE_REMOTE")
    if not isinstance(records, list) or not records:
        raise ValueError("EMPTY_INVENTORY_IS_NOT_DELETION_AUTHORITY")
    sources = {s["source_id"]: s for s in [*prior_sources, *registry["sources"]]
               if s["path"] != "amx_drive:ENROLLMENT_REQUIRED.txt"}
    seen=set()
    for item in records:
        if item.get("IsDir"):
            continue
        identity = item.get("OriginalID") or item.get("ID")
        path = item.get("Path")
        if not identity or not path:
            raise ValueError("STABLE_DRIVE_SOURCE_ID_REQUIRED")
        sid = "drive-" + hashlib.sha256(str(identity).encode()).hexdigest()[:32]
        if sid in seen:
            raise ValueError("CONFLICTING_DRIVE_INVENTORY_ID")
        seen.add(sid)
        old = sources.get(sid)
        row = {"source_id":sid,"source_system":"google_drive","path":remote+path,
               "source_identifier":str(identity),"project":"UNCLASSIFIED",
               "classification":"SOURCE_ASSET","classification_state":"UNKNOWN",
               "authority_level":"REFERENCE","adapter":"rclone_drive","required":False,
               "encryption_required":True,"recovery_priority":3,
               "retention_policy":"Inherited encrypted generation retention",
               "supersession_state":"UNKNOWN","authority_receipt":"Owner-approved scoped Drive continuity enrollment",
               "export_name":"source.export","current_version":item.get("ModTime"),
               "last_observed_at":None,"last_successful_mirror_at":None,"mirror_location":None,
               "integrity_result":"UNKNOWN","restoration_test_state":"UNKNOWN","last_readback_result":None}
        if old:
            # Retain accepted classification/authority even if provider metadata changes.
            row = {**old, "path":remote+path, "current_version":item.get("ModTime")}
        for field in ["last_observed_at", "last_successful_mirror_at", "mirror_location", "current_hash", "last_readback_result"]:
            if field in row:
                row[field] = None
        row.update(integrity_result="UNKNOWN", restoration_test_state="UNKNOWN")
        sources[sid]=row
    if not seen:
        raise ValueError("NO_RECOVERABLE_DRIVE_FILES")
    data = {k:v for k,v in registry.items() if k != "registry_sha256"}
    data["sources"] = sorted(sources.values(),key=lambda s:s["source_id"])
    data["registry_sha256"] = hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return data


def discover_scoped_drive(registry: dict, remote: str, config_file: str, prior_sources: list[dict]) -> dict:
    from .continuity import private_file
    from pathlib import Path
    conf=private_file(Path(config_file))
    result=subprocess.run(["rclone","lsjson",remote,"--recursive","--files-only","--config",str(conf),
        "--drive-export-formats","txt,xlsx,pdf","--retries","1","--low-level-retries","1",
        "--contimeout","10s","--timeout","30s"],capture_output=True,timeout=60)
    if result.returncode:
        raise ValueError("DRIVE_INVENTORY_UNAVAILABLE")
    if len(result.stdout)>64*1024*1024:
        raise ValueError("INVENTORY_REQUIRES_BOUNDED_SCOPE")
    return drive_inventory(registry,json.loads(result.stdout),remote,prior_sources)
