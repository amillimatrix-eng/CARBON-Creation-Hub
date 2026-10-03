#!/usr/bin/env python3
"""One-shot BLACK continuity operations, supervised by standard systemd."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.continuity import RecoveryStore, load_registry, now, atomic, private_file
from backend.security import authorize, local_grants
from cryptography.fernet import Fernet


def configured_store() -> RecoveryStore:
    if not os.environ.get("AMX_CONTINUITY_ROOT") or not os.environ.get("AMX_CONTINUITY_KEY_FILE"):
        raise ValueError("CONTINUITY_ENROLLMENT_REQUIRED")
    return RecoveryStore(Path(os.environ["AMX_CONTINUITY_ROOT"]), Path(os.environ["AMX_CONTINUITY_KEY_FILE"]), ROOT)


def operation(action: str, target: Path | None = None, snapshot: str | None = None) -> dict:
    grants = local_grants(ROOT)
    scopes = {"sync": "continuity_sync", "verify": "continuity_verify",
              "restore-test": "continuity_restore_test", "health": "continuity_health"}
    authorize(grants, "BLACK", "read_governance", scopes.get(action, "continuity_restore_test"))
    authorize(grants, "BLACK", "write_receipts", "continuity")
    authorize(grants, "BLACK", "access_credentials", "continuity-key-and-drive-read-only")
    authorize(grants, "BLACK", "read_private_assets", "continuity-mirror-and-isolated-restore")
    store = configured_store()
    if action == "sync":
        authorize(grants, "BLACK", "access_network", "drive-read-only-scoped-remote")
        path = Path(os.environ.get("AMX_SOURCE_REGISTRY", ROOT / "CONTINUITY/source-registry.json"))
        registry = load_registry(path, ROOT, os.environ.get("AMX_SOURCE_REGISTRY_SHA256"))
        if os.environ.get("AMX_DRIVE_DISCOVERY_REMOTE"):
            from backend.sources import discover_scoped_drive
            prior = store._read(store.root / "observations.enc", {}).get("sources", [])
            # Keep only registry fields, not derived mirror observation fields.
            schema = json.loads((ROOT / "CONTINUITY/source-registry.schema.json").read_text())
            allowed = set(schema["properties"]["sources"]["items"]["properties"])
            prior = [{k:v for k,v in s.items() if k in allowed} for s in prior]
            try:
                registry = discover_scoped_drive(registry, os.environ["AMX_DRIVE_DISCOVERY_REMOTE"], os.environ["AMX_RCLONE_CONFIG_FILE"], prior)
            except Exception:
                # Discoverer outage must not prevent registered local sources from syncing.
                # Retain earlier discovered sources so deletion never erases the inventory.
                registry["sources"].extend(s for s in prior if s["source_id"] not in {r["source_id"] for r in registry["sources"]})
        result = store.sync(registry)
        if result["promoted"]:
            store.verify()
            store.restore_test()
            store.prune(registry["retention"]["keep_last"], registry["retention"]["days"])
        return result
    if action == "verify":
        return store.verify(snapshot)
    if action == "restore-test":
        return store.restore_test()
    if action == "restore":
        if target is None:
            raise ValueError("CLEAN_RESTORE_TARGET_REQUIRED")
        return store.restore(target, snapshot)
    if action == "replicate":
        if target is None:
            raise ValueError("INDEPENDENT_REPLICA_TARGET_REQUIRED")
        return store.replicate(target)
    if action == "health":
        return store.health()
    raise ValueError("UNSUPPORTED_OPERATION")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["sync", "verify", "restore-test", "restore", "health", "replicate", "init-key"])
    parser.add_argument("--target", type=Path)
    parser.add_argument("--snapshot")
    args = parser.parse_args()
    try:
        if args.action == "init-key":
            if args.target is None or args.target.exists() or ROOT in args.target.resolve().parents:
                raise ValueError("NEW_KEY_OUTSIDE_GIT_REQUIRED")
            args.target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            atomic(args.target, Fernet.generate_key()+b"\n", immutable=True)
            result = {"state": "PASS", "action": "KEY_CREATED", "key_value_disclosed": False,
                      "remaining_gate": "ESCROW_KEY_ON_INDEPENDENT_OFFLINE_CUSTODY"}
        else:
            result = operation(args.action, args.target, args.snapshot)
        print(json.dumps(result, sort_keys=True))
        return 0 if result.get("state") == "PASS" else 2
    except Exception as exc:
        # Errors may embed URLs/tokens; only their class is public.
        print(json.dumps({"state": "HOLD", "action": args.action, "error_type": type(exc).__name__, "at": now()}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
