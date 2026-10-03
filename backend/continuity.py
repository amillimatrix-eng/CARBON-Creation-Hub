"""Encrypted recovery for existing AMX sources; never an authority promotion path.

Fernet is provided by cryptography. This module implements storage/verification,
not cryptographic primitives. Private payloads and manifests never enter Git.
"""
from __future__ import annotations

import contextlib
import fcntl
import hashlib
import io
import json
import os
import re
import shutil
import sqlite3
import stat
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from jsonschema import validate

CHUNK = 4 * 1024 * 1024
HEX = re.compile(r"^[a-f0-9]{64}$")
SID = re.compile(r"^[A-Za-z0-9_-]{1,80}$")
PUBLIC_FIELDS = {
    "schema", "state", "source_commit", "config_sha256", "last_matrix_sync",
    "last_verified_backup", "backup_age_seconds", "last_restore_test",
    "last_integrity_check", "integrity_failures", "source_failures",
    "active_recovery_snapshot", "unresolved_holds", "security_warnings",
    "provider_availability", "worker_runtime_state", "last_material_receipt",
    "capability_version", "worker_stagnation", "observed_at",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative(name: str) -> Path:
    p = PurePosixPath(name)
    if not name or p.is_absolute() or any(x in {".", ".."} for x in name.split("/")) or "\\" in name or "\0" in name:
        raise ValueError("UNSAFE_RELATIVE_PATH")
    return Path(*p.parts)


def private_file(path: Path) -> Path:
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("SECRET_FILE_REQUIRED")
    s = path.stat()
    if s.st_mode & 0o077 or s.st_uid not in {os.getuid(), 0}:
        raise PermissionError("SECRET_FILE_PERMISSIONS")
    return path


def atomic(path: Path, data: bytes, immutable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.is_symlink():
        raise ValueError("SYMLINK_DESTINATION")
    fd, temporary = tempfile.mkstemp(prefix=".pending-", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        if immutable:
            os.link(temporary, path)  # create-only; never replace an accepted generation
            os.unlink(temporary)
        else:
            os.replace(temporary, path)
        dfd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    finally:
        Path(temporary).unlink(missing_ok=True)


def git_version(root: Path) -> dict[str, Any]:
    def run(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True, timeout=10).stdout.strip()
    try:
        return {"commit": run("rev-parse", "HEAD"), "dirty": bool(run("status", "--porcelain"))}
    except (OSError, subprocess.SubprocessError):
        return {"commit": "UNKNOWN", "dirty": True}


def load_registry(path: Path, repo: Path, expected_hash: str | None = None) -> dict[str, Any]:
    raw = path.read_bytes()
    if expected_hash and digest(raw) != expected_hash:
        raise ValueError("REGISTRY_AUTHORITY_HASH_MISMATCH")
    data = json.loads(raw)
    schema = json.loads((repo / "CONTINUITY/source-registry.schema.json").read_text())
    validate(data, schema)
    ids = [s["source_id"] for s in data["sources"]]
    if len(ids) != len(set(ids)):
        raise ValueError("DUPLICATE_SOURCE_ID")
    data["registry_sha256"] = digest(raw)
    return data


class RecoveryStore:
    def __init__(self, root: Path, key_file: Path, repo: Path):
        self.root = Path(root).absolute()
        self.repo = Path(repo).resolve()
        if self.root.is_symlink() or self.root == self.repo or self.repo in self.root.parents:
            raise ValueError("RECOVERY_STORE_MUST_BE_OUTSIDE_GIT")
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        if self.root.stat().st_mode & 0o077:
            raise PermissionError("RECOVERY_STORE_PERMISSIONS")
        self.key_file = private_file(key_file)
        if self.root == self.key_file.resolve() or self.root in self.key_file.resolve().parents:
            raise ValueError("KEY_MUST_NOT_ACCOMPANY_CIPHERTEXT_REPLICA")
        if self.repo in self.key_file.resolve().parents:
            raise ValueError("KEY_MUST_BE_OUTSIDE_GIT")
        self.cipher = Fernet(self.key_file.read_bytes().strip())
        for name in ["chunks", "snapshots", "receipts"]:
            p = self.root / name
            if p.is_symlink():
                raise ValueError("SYMLINK_STORE_DIRECTORY")
            p.mkdir(exist_ok=True, mode=0o700)

    @contextlib.contextmanager
    def lock(self):
        p = self.root / "operation.lock"
        if p.is_symlink():
            raise ValueError("SYMLINK_LOCK")
        fd = os.open(p, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "a") as f:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                yield
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    def _write(self, path: Path, value: Any, immutable: bool = False) -> None:
        atomic(path, self.cipher.encrypt(canonical(value)), immutable)

    def _read(self, path: Path, default: Any = None) -> Any:
        if not path.exists():
            return default
        if path.is_symlink():
            raise ValueError("SYMLINK_ENCRYPTED_FILE")
        return json.loads(self.cipher.decrypt(path.read_bytes()))

    def _receipt(self, action: str, state: str, evidence: dict[str, Any]) -> dict[str, Any]:
        # Scan the immutable chain so a crash between append and head update resumes safely.
        chain = self.read_receipts()
        previous = chain[-1]["sha256"] if chain else None
        body = {"schema": "AMX.CONTINUITY.RECEIPT.v1", "sequence": len(chain) + 1,
                "action": action, "state": state, "at": now(), "previous_sha256": previous,
                "source_version": git_version(self.repo), "evidence": evidence}
        h = digest(canonical(body))
        receipt = {**body, "sha256": h}
        self._write(self.root / "receipts" / f"{len(chain)+1:012d}-{h}.enc", receipt, True)
        self._write(self.root / "receipt-head.enc", {"sha256": h, "sequence": len(chain)+1})
        return receipt

    def read_receipts(self) -> list[dict[str, Any]]:
        chain: list[dict[str, Any]] = []
        previous = None
        for p in sorted((self.root / "receipts").glob("*.enc")):
            r = self._read(p)
            content = {k: v for k, v in r.items() if k != "sha256"}
            if digest(canonical(content)) != r["sha256"] or r["previous_sha256"] != previous or r["sequence"] != len(chain)+1:
                raise ValueError("RECEIPT_CHAIN_CORRUPT")
            previous = r["sha256"]
            chain.append(r)
        anchor = self._read(self.root / "receipt-head.enc")
        if anchor and (anchor["sequence"] > len(chain) or chain[anchor["sequence"]-1]["sha256"] != anchor["sha256"]):
            raise ValueError("RECEIPT_CHAIN_TRUNCATED")
        return chain

    def _chunk(self, data: bytes) -> str:
        h = digest(data)
        path = self.root / "chunks" / f"{h}.enc"
        if path.exists():
            if digest(self.cipher.decrypt(path.read_bytes())) != h:
                raise ValueError("EXISTING_CHUNK_CORRUPT")
        else:
            atomic(path, self.cipher.encrypt(data), True)
        return h

    def _capture(self, name: str, stream) -> dict[str, Any]:
        relative(name)
        h = hashlib.sha256()
        chunks = []
        size = 0
        while data := stream.read(CHUNK):
            size += len(data)
            h.update(data)
            chunks.append(self._chunk(data))
        return {"path": name, "sha256": h.hexdigest(), "bytes": size, "chunks": chunks}

    def _safe_local(self, source: dict[str, Any]) -> Path:
        raw = Path(source["path"])
        allowed = Path(source.get("allowed_root", str(self.repo))).resolve()
        p = raw if raw.is_absolute() else allowed / raw
        # Resolve every component only after rejecting symbolic links.
        for part in [p, *p.parents]:
            if part.is_symlink():
                raise ValueError("SOURCE_SYMLINK")
        p = p.resolve()
        if p != allowed and allowed not in p.parents:
            raise ValueError("SOURCE_OUTSIDE_ALLOWED_ROOT")
        if p == self.root or self.root in p.parents or p == self.key_file.resolve():
            raise ValueError("RECOVERY_OR_KEY_AS_SOURCE")
        return p

    def _source(self, source: dict[str, Any]) -> list[dict[str, Any]]:
        adapter = source["adapter"]
        files = []
        if adapter == "rclone_drive":
            conf = private_file(Path(os.environ["AMX_RCLONE_CONFIG_FILE"]))
            locator = source["path"]
            if not re.fullmatch(r"[A-Za-z0-9_-]+:.+", locator) or any(x in locator for x in ["\n", "\r", "\0"]):
                raise ValueError("INVALID_RCLONE_LOCATOR")
            # Streaming avoids a second plaintext Drive copy on disk.
            cmd = ["rclone", "cat", locator, "--config", str(conf), "--drive-export-formats", "txt,xlsx,pdf",
                   "--retries", "1", "--low-level-retries", "1", "--contimeout", "10s", "--timeout", "30s"]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            try:
                files.append(self._capture(source.get("export_name", "source.export"), proc.stdout))
                if proc.wait(timeout=45) != 0:
                    raise ValueError("DRIVE_READ_FAILED")
            finally:
                if proc.poll() is None:
                    proc.kill()
                proc.wait()
        elif adapter == "sqlite_backup":
            p = self._safe_local(source)
            with sqlite3.connect(p.as_uri()+"?mode=ro", uri=True) as src, sqlite3.connect(":memory:") as dst:
                src.backup(dst)
                files.append(self._capture(p.name, io.BytesIO(dst.serialize())))
        elif adapter in {"local", "git_tree"}:
            p = self._safe_local(source)
            if adapter == "git_tree":
                names = subprocess.run(["git", "ls-files", "-z"], cwd=p, check=True, capture_output=True, timeout=20).stdout.split(b"\0")
                paths = [(n.decode(), p / relative(n.decode())) for n in names if n]
            else:
                paths = [(p.name, p)] if p.is_file() else [(x.relative_to(p).as_posix(), x) for x in sorted(p.rglob("*")) if x.is_file() or x.is_symlink()]
            if not paths:
                raise ValueError("EMPTY_SOURCE")
            for name, file in paths:
                for part in [file, *file.parents]:
                    if part.is_symlink():
                        raise ValueError("SOURCE_SYMLINK")
                if not file.is_file():
                    raise ValueError("SOURCE_NOT_REGULAR")
                before = file.stat()
                with file.open("rb") as stream:
                    files.append(self._capture(name, stream))
                after = file.stat()
                if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
                    raise ValueError("CONFLICTING_SOURCE_WRITE")
        else:
            raise ValueError("UNSUPPORTED_SOURCE_ADAPTER")
        expected = source.get("expected_sha256")
        if expected and (len(files) != 1 or files[0]["sha256"] != expected):
            raise ValueError("SOURCE_AUTHORITY_HASH_MISMATCH")
        return files

    def _manifest(self, snapshot: str) -> dict[str, Any]:
        if not HEX.fullmatch(snapshot):
            raise ValueError("INVALID_SNAPSHOT_ID")
        m = self._read(self.root / "snapshots" / f"{snapshot}.enc")
        if not m or digest(canonical(m["content"])) != snapshot or m["content"]["role"] != "MIRROR_RECOVERY":
            raise ValueError("MANIFEST_INTEGRITY_FAILED")
        return m

    def _data(self, f: dict[str, Any]):
        relative(f["path"])
        h = hashlib.sha256()
        size = 0
        for chunk in f["chunks"]:
            if not HEX.fullmatch(chunk):
                raise ValueError("INVALID_CHUNK_ID")
            p = self.root / "chunks" / f"{chunk}.enc"
            if p.is_symlink():
                raise ValueError("CHUNK_SYMLINK")
            data = self.cipher.decrypt(p.read_bytes())
            if len(data) > CHUNK or digest(data) != chunk:
                raise ValueError("CHUNK_HASH_FAILED")
            size += len(data)
            h.update(data)
            yield data
        if h.hexdigest() != f["sha256"] or size != f["bytes"]:
            raise ValueError("FILE_HASH_FAILED")

    def _verify(self, snapshot: str) -> dict[str, Any]:
        m = self._manifest(snapshot)
        count = 0
        seen = set()
        for s in m["content"]["sources"]:
            if not SID.fullmatch(s["source_id"]):
                raise ValueError("INVALID_SOURCE_ID")
            for f in s["files"]:
                key = s["source_id"] + "/" + f["path"]
                if key in seen:
                    raise ValueError("DUPLICATE_RESTORE_PATH")
                seen.add(key)
                for _ in self._data(f):
                    pass
                count += 1
        return {"snapshot": snapshot, "files_verified": count, "manifest_sha256": snapshot,
                "authority_rule": "MIRROR_RECOVERY_IS_NOT_GOVERNANCE", "state": "PASS"}

    def sync(self, registry: dict[str, Any]) -> dict[str, Any]:
        with self.lock():
            sources = []
            failures = []
            observed = []
            prior_observations = {s["source_id"]: s for s in self._read(self.root / "observations.enc", {}).get("sources", [])}
            for s in sorted(registry["sources"], key=lambda x: x["source_id"]):
                try:
                    files = self._source(s)
                    sources.append({**s, "files": files})
                    observed.append({**s, "last_observed_at": now(), "last_successful_mirror_at": now(),
                        "current_hash": digest(canonical(files)), "mirror_location": "ENCRYPTED_CONTENT_ADDRESSED",
                        "integrity_result": "PASS", "last_readback_result": "CAPTURE_HASH_VERIFIED",
                        "restoration_test_state": "NOT_YET_TESTED"})
                except (Exception,) as exc:
                    # Persist failure classes, never credential values, command output or exception messages.
                    failures.append({"source_id": s["source_id"], "required": s["required"], "error_type": type(exc).__name__})
                    observed.append({**s, **prior_observations.get(s["source_id"], {}),
                                     "last_observed_at": now(), "integrity_result": "HOLD",
                                     "last_readback_result": "SOURCE_UNAVAILABLE_PRIOR_MIRROR_PRESERVED"})
            content = {"schema": "AMX.RECOVERY.SNAPSHOT.v1", "role": "MIRROR_RECOVERY",
                       "registry_sha256": registry["registry_sha256"], "sources": sources,
                       "source_version": git_version(self.repo), "source_failures": failures}
            snapshot = digest(canonical(content))
            path = self.root / "snapshots" / f"{snapshot}.enc"
            if not path.exists():
                self._write(path, {"content": content, "observed_at": now()}, True)
            try:
                result = self._verify(snapshot)
            except Exception as exc:
                self._receipt("SYNC_VERIFY", "FAIL", {"snapshot": snapshot, "error_type": type(exc).__name__})
                raise
            required_failed = any(f["required"] for f in failures)
            status = self._read(self.root / "status.enc", {})
            status.update(last_matrix_sync=now(), last_integrity_check=now(), source_failures=len(failures),
                          config_sha256=registry["registry_sha256"], source_commit=git_version(self.repo)["commit"])
            if sources and not required_failed:
                self._write(self.root / "latest.enc", {"snapshot": snapshot, "verified_at": now()})
                status.update(last_verified_backup=now(), active_recovery_snapshot=snapshot)
            classification_pending = any(s.get("classification_state") == "UNKNOWN" for s in registry["sources"])
            state = "HOLD" if failures or not sources or classification_pending else "PASS"
            status["state"] = state
            status["unresolved_holds"] = (["SOURCE_UNAVAILABLE"] if failures else []) + (["SOURCE_CLASSIFICATION_GOVERNANCE_PENDING"] if classification_pending else [])
            status["provider_availability"] = {system: ("DEGRADED" if any(f["source_id"]==s["source_id"] for s in registry["sources"] if s["source_system"]==system for f in failures) else "READBACK_PROVEN") for system in {s["source_system"] for s in registry["sources"]}}
            self._write(self.root / "observations.enc", {"sources": observed, "failures": failures, "snapshot": snapshot})
            r = self._receipt("SYNC", state, {**result, "source_failures": failures, "promoted": bool(sources and not required_failed)})
            status["last_material_receipt"] = r["sha256"]
            self._write(self.root / "status.enc", status)
            self.publish_health()
            return {**result, "state": state, "promoted": bool(sources and not required_failed), "receipt_sha256": r["sha256"], "source_failures": len(failures)}

    def latest_verified(self) -> str:
        pointer = self._read(self.root / "latest.enc")
        if not pointer:
            raise ValueError("NO_VERIFIED_RECOVERY_SNAPSHOT")
        self._verify(pointer["snapshot"])
        return pointer["snapshot"]

    def verify(self, snapshot: str | None = None) -> dict[str, Any]:
        with self.lock():
            try:
                result = self._verify(snapshot or self.latest_verified())
            except Exception as exc:
                r = self._receipt("INTEGRITY", "FAIL", {"error_type": type(exc).__name__})
                status = self._read(self.root / "status.enc", {})
                status.update(state="HOLD", last_integrity_check=now(), integrity_failures=status.get("integrity_failures", 0)+1, last_material_receipt=r["sha256"], unresolved_holds=["CORRUPT_RECOVERY"])
                self._write(self.root / "status.enc", status)
                self.publish_health()
                raise
            r = self._receipt("INTEGRITY", "PASS", result)
            status = self._read(self.root / "status.enc", {})
            status.update(last_integrity_check=now(), last_material_receipt=r["sha256"])
            self._write(self.root / "status.enc", status)
            self.publish_health()
            return {**result, "receipt_sha256": r["sha256"]}

    def restore(self, target: Path, snapshot: str | None = None) -> dict[str, Any]:
        with self.lock():
            target = Path(target).absolute()
            if target.exists() or target.is_symlink() or any(p.is_symlink() for p in target.parents):
                raise ValueError("RESTORE_REQUIRES_CLEAN_TARGET")
            if self.repo == target or self.repo in target.parents or self.root == target or self.root in target.parents:
                raise ValueError("RESTORE_MUST_NOT_TOUCH_LIVE_AUTHORITY")
            staging = None
            try:
                snapshot = snapshot or self.latest_verified()
                result = self._verify(snapshot)
                manifest = self._manifest(snapshot)
                target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                staging = Path(tempfile.mkdtemp(prefix=".amx-restore-", dir=target.parent))
                for source in manifest["content"]["sources"]:
                    for file in source["files"]:
                        p = staging / source["source_id"] / relative(file["path"])
                        p.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                        with p.open("xb") as output:
                            os.chmod(p, 0o600)
                            for data in self._data(file):
                                output.write(data)
                            output.flush()
                            os.fsync(output.fileno())
                        if digest(p.read_bytes()) != file["sha256"]:
                            raise ValueError("RESTORE_COMPARE_FAILED")
                atomic(staging / ".amx-restoration.json", canonical({"snapshot": snapshot,
                    "role": "MIRROR_RECOVERY", "source_authority_retained": True,
                    "automatic_authority_promotion": False, "manifest": manifest}))
                os.rename(staging, target)
                staging = None
                r = self._receipt("RESTORE_COMPARE", "PASS", result)
                status = self._read(self.root / "status.enc", {})
                status.update(last_restore_test=now(), last_restore_snapshot=snapshot, last_material_receipt=r["sha256"])
                self._write(self.root / "status.enc", status)
                observations = self._read(self.root / "observations.enc", {})
                if observations.get("snapshot") == snapshot:
                    for s in observations.get("sources", []):
                        s["restoration_test_state"] = "PASS"
                    self._write(self.root / "observations.enc", observations)
                self.publish_health()
                return {**result, "receipt_sha256": r["sha256"], "compared": True}
            except Exception as exc:
                self._receipt("RESTORE_COMPARE", "FAIL", {"error_type": type(exc).__name__})
                raise
            finally:
                if staging:
                    shutil.rmtree(staging)

    def restore_test(self) -> dict[str, Any]:
        with tempfile.TemporaryDirectory(prefix="amx-restore-test-") as tmp:
            return self.restore(Path(tmp) / "reconstructed")

    def prune(self, keep_last: int = 7, retention_days: int = 30) -> dict[str, Any]:
        if keep_last < 1 or retention_days < 1:
            raise ValueError("RETENTION_MUST_PRESERVE_HISTORY")
        with self.lock():
            entries = [(p, self._manifest(p.stem)) for p in (self.root / "snapshots").glob("*.enc")]
            entries.sort(key=lambda pair: pair[1]["observed_at"], reverse=True)
            protected = {self.latest_verified(), self._read(self.root / "status.enc", {}).get("last_restore_snapshot")}
            cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
            retained = []
            removed = 0
            for i, (p, m) in enumerate(entries):
                if i < keep_last or p.stem in protected or datetime.fromisoformat(m["observed_at"]) >= cutoff:
                    retained.append(m)
                else:
                    p.unlink()
                    removed += 1
            referenced = {c for m in retained for s in m["content"]["sources"] for f in s["files"] for c in f["chunks"]}
            for p in (self.root / "chunks").glob("*.enc"):
                if p.stem not in referenced:
                    p.unlink()
            r = self._receipt("RETENTION", "PASS", {"snapshots_removed": removed, "snapshots_retained": len(retained)})
            return {"state": "PASS", "removed": removed, "receipt_sha256": r["sha256"]}

    def replicate(self, target: Path, require_independent_device: bool = True) -> dict[str, Any]:
        with self.lock():
            target = Path(target).absolute()
            if target.exists() or target.is_symlink() or self.root in target.parents or any(p.is_symlink() for p in target.parents):
                raise ValueError("REPLICA_REQUIRES_NEW_INDEPENDENT_TARGET")
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            if require_independent_device and target.parent.stat().st_dev == self.root.stat().st_dev:
                raise ValueError("REPLICA_DEVICE_NOT_INDEPENDENT")
            self.latest_verified()
            shutil.copytree(self.root, target, ignore=shutil.ignore_patterns("operation.lock", "public-health.json", ".pending-*"))
            os.chmod(target, 0o700)
            copy = RecoveryStore(target, self.key_file, self.repo)
            copy.latest_verified()
            r = self._receipt("CIPHERTEXT_REPLICATION", "PASS", {"independent_device": require_independent_device})
            return {"state": "PASS", "receipt_sha256": r["sha256"]}

    def health(self, stale_after_seconds: int = 86400) -> dict[str, Any]:
        status = self._read(self.root / "status.enc", {})
        result = {k: v for k, v in status.items() if k in PUBLIC_FIELDS}
        result.update(schema="AMX.CONTINUITY.HEALTH.v1", observed_at=now(),
                      capability_version="continuity-v1", worker_runtime_state="RECOVERY_SERVICE_READBACK_ONLY",
                      security_warnings=[], worker_stagnation="UNKNOWN")
        date = result.get("last_verified_backup")
        result["backup_age_seconds"] = max(0, int((datetime.now(timezone.utc)-datetime.fromisoformat(date)).total_seconds())) if date else None
        if not date or result["backup_age_seconds"] > stale_after_seconds:
            result["state"] = "HOLD"
            result["unresolved_holds"] = sorted(set(result.get("unresolved_holds", [])+["MISSING_OR_STALE_BACKUP"]))
        result.setdefault("integrity_failures", 0)
        result.setdefault("provider_availability", {})
        return result

    def publish_health(self) -> None:
        atomic(self.root / "public-health.json", canonical(self.health()))


def safe_health(path: Path | None) -> dict[str, Any]:
    if not path or not Path(path).exists():
        return {"schema": "AMX.CONTINUITY.HEALTH.v1", "state": "HOLD",
                "unresolved_holds": ["BLACK_CONTINUITY_READBACK_NOT_ENROLLED"],
                "active_recovery_snapshot": None, "source_commit": "UNKNOWN"}
    try:
        data = json.loads(Path(path).read_text())
        out = {k: v for k, v in data.items() if k in PUBLIC_FIELDS}
        # A producer outage must not preserve an apparently healthy label forever.
        age = (datetime.now(timezone.utc)-datetime.fromisoformat(out["observed_at"])).total_seconds()
        if age > 86400 or age < -300:
            out.update(state="HOLD", unresolved_holds=["STALE_OR_INVALID_HEALTH_READBACK"])
        return out
    except (ValueError, KeyError, TypeError):
        return {"schema": "AMX.CONTINUITY.HEALTH.v1", "state": "HOLD", "unresolved_holds": ["INVALID_HEALTH_READBACK"]}
